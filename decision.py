
"""
Decision Layer: Plans the execution strategy based on perception and memory
Non-Deterministic: Uses LLM for planning and decision-making
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from perception import PerceivedQuery
from memory import MemoryContext
from google import genai
import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


# Pydantic Models
class ToolCall(BaseModel):
    """Represents a single tool call decision"""
    tool_name: str = Field(description="Name of tool to call")
    arguments: dict[str, Any] = Field(description="Arguments for the tool")
    reasoning: str = Field(description="Why this tool is being called")


class DecisionOutput(BaseModel):
    """Output from decision layer"""
    action_type: Literal["tool_call", "final_answer", "error"] = Field(
        description="Type of action to take"
    )
    tool_call: Optional[ToolCall] = None
    final_answer: Optional[str] = None
    error_message: Optional[str] = None
    reasoning_steps: list[str] = Field(default_factory=list)
    should_continue: bool = Field(default=True, description="Whether to continue loop")


class DecisionLayer:
    """Decision cognitive layer - plans execution strategy"""

    def __init__(self):
        self.client = client
        self.conversation_history = []
    def _build_decision_prompt(
            self,
            perceived: PerceivedQuery,
            memory: MemoryContext,
            tool_result: Optional[str] = None
        ) -> str:
        """Build prompt for decision-making LLM with full reasoning and error handling"""

        # --- USER PREFERENCES CONTEXT ---
        user_prefs = f"""
                        USER PREFERENCES (from memory):
                        - Name: {memory.preferences.name}
                        - Explanation Style: {memory.preferences.preferred_explanation_style}
                        - Preferred Method: {memory.preferences.preferred_method}
                        - Math Level: {memory.preferences.math_level}
                        - Show Reasoning: {memory.preferences.show_reasoning}
                        - Verification Required: {memory.preferences.verification_required}

                        PERSONALIZATION (for communication or email):
                        - Font Style: {memory.preferences.font_style}
                        - Font Color: {memory.preferences.font_color}
                        - Communication Tone: {memory.preferences.communication_tone}
                        - Signature: {memory.preferences.signature}
                        """

        # --- PERCEIVED CONTEXT ---
        problem_context = f"""
                            PERCEIVED PROBLEM:
                            - Type: {perceived.problem_type}
                            - Expression: {perceived.expression}
                            - Variable: {perceived.variable}
                            - Features: {json.dumps(perceived.key_features)}
                            """

        session_context = f"""
                        SESSION STATE:
                        - Iteration: {memory.session.iteration_count}
                        - Parsed Terms: {memory.session.parsed_terms}
                        - Integrated Terms Count: {len(memory.session.integrated_terms)}
                        - Differentiated Terms Count: {len(memory.session.differentiated_terms)}
                        """

        # --- ALREADY INTEGRATED TERMS ---
        integrated_terms_context = ""
        if memory.session.integrated_terms:
            integrated_terms_context = f"""
                ALREADY INTEGRATED TERMS:
                {memory.session.integrated_terms}
                Ensure that these terms are NOT integrated again.
            """

        tool_context = f"\nLAST TOOL RESULT:\n{tool_result}\n" if tool_result else ""

        # --- TOOL CONTEXT AND WORKFLOW ---
        workflow_guidance = f"""
                            AVAILABLE TOOLS:
                            1. show_reasoning(steps: list)
                            2. parse_polynomial(expression: str)
                            3. integrate_term(coeff: float, power: float)
                            4. differentiate_term(coeff: float, power: float)
                            5. format_polynomial_latex(terms: list)
                            6. compare_polynomials(original: list, verified: list)
                            7. integrate_symbolic(expression: str, variable: str)
                            8. differentiate_symbolic(expression: str, variable: str)
                            9. verify_symbolic_integration(original: str, antiderivative: str, variable: str)
                            10. send_gmail_text_personalized(to: str,subject: str,body: str,font_style: str = "Arial",font_color: str = "black",signature: str = "",tone: str = "friendly",sender: str = "me")

                            DECISION RULES:
                            - Choose polynomial or symbolic workflow depending on problem type and user preference.
                            - Always separate reasoning steps from tool calls.
                            - Show step-by-step reasoning, and tag each step with reasoning type (arithmetic, symbolic, logic, verification, communication, etc.)
                            - Before finalizing, perform internal sanity checks:
                            • Verify calculations or derivations using available tools.
                            • Confirm that previously integrated terms are not repeated.
                            • Cross-check intermediate results where possible.
                            - If verification_required=True, run verification tools before final answer.
                            - For any communication task (emails, summaries):
                            • Respect user font, color, and tone preferences.
                            • Include signature.
                            • Format message as styled plain text or HTML.
                            - If uncertain, provide a clear error explanation instead of guessing.

                            EXAMPLE EMAIL STYLE:
                            If tone={memory.preferences.communication_tone}, font={memory.preferences.font_style}, color={memory.preferences.font_color}, signature="{memory.preferences.signature}":
                            Body Example:
                            <p style="font-family: {memory.preferences.font_style}; color: {memory.preferences.font_color};">
                            Here is the integration result you requested:<br><br>
                            {perceived.expression} = [calculated_result]<br><br>
                            {memory.preferences.signature}
                            </p>

                            OUTPUT FORMAT (JSON only):
                            {{
                            "action_type": "tool_call" | "final_answer" | "error",
                            "tool_call": {{
                                "tool_name": "<name>",
                                "arguments": {{<args>}},
                                "reasoning": "<why this tool>",
                                "reasoning_type": "<arithmetic|symbolic|logic|verification|communication>"
                            }},
                            "reasoning_steps": ["step1", "step2", "..."],
                            "internal_checks": ["check1", "check2"],
                            "fallbacks": ["fallback_action_if_any"],
                            "should_continue": true/false
                            }}

                            OR for final answer:
                            {{
                            "action_type": "final_answer",
                            "final_answer": "[LaTeX expression + C]",
                            "reasoning_steps": ["summary"],
                            "internal_checks": ["sanity verification completed"],
                            "fallbacks": [],
                            "should_continue": false
                            }}

                            OR for error/fallback:
                            {{
                            "action_type": "error",
                            "message": "<explanation of issue or uncertainty>",
                            "reasoning_steps": ["steps attempted"],
                            "internal_checks": ["sanity checks performed"],
                            "fallbacks": ["next recommended action"],
                            "should_continue": false
                            }}
                        """

        return f"""{user_prefs}
                    {problem_context}
                    {session_context}
                    {integrated_terms_context}
                    {tool_context}
                    {workflow_guidance}

                    Now, based on ALL context above (especially personalization preferences), decide the NEXT SINGLE ACTION.
                    Respond ONLY in JSON format:
                """

    # def _build_decision_prompt(
    #     self,
    #     perceived: PerceivedQuery,
    #     memory: MemoryContext,
    #     tool_result: Optional[str] = None
    # ) -> str:
    #     """Build prompt for decision-making LLM"""

    #     # --- USER PREFERENCES CONTEXT ---
    #     user_prefs = f"""
    #                     USER PREFERENCES (from memory):
    #                     - Name: {memory.preferences.name}
    #                     - Explanation Style: {memory.preferences.preferred_explanation_style}
    #                     - Preferred Method: {memory.preferences.preferred_method}
    #                     - Math Level: {memory.preferences.math_level}
    #                     - Show Reasoning: {memory.preferences.show_reasoning}
    #                     - Verification Required: {memory.preferences.verification_required}

    #                     PERSONALIZATION (for communication or email):
    #                     - Font Style: {memory.preferences.font_style}
    #                     - Font Color: {memory.preferences.font_color}
    #                     - Communication Tone: {memory.preferences.communication_tone}
    #                     - Signature: {memory.preferences.signature}
    #                     """

    #     # --- PERCEIVED CONTEXT ---
    #     problem_context = f"""
    #                         PERCEIVED PROBLEM:
    #                         - Type: {perceived.problem_type}
    #                         - Expression: {perceived.expression}
    #                         - Variable: {perceived.variable}
    #                         - Features: {json.dumps(perceived.key_features)}
    #                         """

    #     session_context = f"""
    #                     SESSION STATE:
    #                     - Iteration: {memory.session.iteration_count}
    #                     - Parsed Terms: {memory.session.parsed_terms}
    #                     - Integrated Terms Count: {len(memory.session.integrated_terms)}
    #                     - Differentiated Terms Count: {len(memory.session.differentiated_terms)}
    #                     """
        
    #     # --- NEW: Already integrated terms context ---
    #     integrated_terms_context = ""
    #     if memory.session.integrated_terms:
    #         integrated_terms_context = f"""
    #             ALREADY INTEGRATED TERMS:
    #             {memory.session.integrated_terms}
    #             Ensure that these terms are NOT integrated again.
    #         """

    #     tool_context = f"\nLAST TOOL RESULT:\n{tool_result}\n" if tool_result else ""

    #     # --- TOOL CONTEXT ---
    #     workflow_guidance = """
    #                         AVAILABLE TOOLS:
    #                         1. show_reasoning(steps: list)
    #                         2. parse_polynomial(expression: str)
    #                         3. integrate_term(coeff: float, power: float)
    #                         4. differentiate_term(coeff: float, power: float)
    #                         5. format_polynomial_latex(terms: list)
    #                         6. compare_polynomials(original: list, verified: list)
    #                         7. integrate_symbolic(expression: str, variable: str)
    #                         8. differentiate_symbolic(expression: str, variable: str)
    #                         9. verify_symbolic_integration(original: str, antiderivative: str, variable: str)
    #                         10. send_gmail_text_personalized(to: str,subject: str,body: str,font_style: str = "Arial",font_color: str = "black",signature: str = "",tone: str = "friendly",sender: str = "me")— Send an email message.

    #                         DECISION RULES:
    #                         - Use polynomial or symbolic workflows depending on problem type and user preference.
    #                         - Respect user explanation style, method, and math level.
    #                         - If verification_required=True, verify before final answer.
    #                         - If task involves communication (e.g., sending an email or summarizing results):
    #                         - Use user’s font style and font color for formatting.
    #                         - Match the user’s communication tone:
    #                             • "friendly" → use warm and conversational phrasing
    #                             • "professional" → use formal and polite language
    #                             • "casual" → keep short and relaxed
    #                         - Always include user’s signature at the end.
    #                         - Format the email body as an HTML or styled plain text message.
    #                         - Prefer `send_gmail_text_personalized` tool for sending such messages.

    #                         EXAMPLE EMAIL STYLE:
    #                         If tone={memory.preferences.communication_tone}, font={memory.preferences.font_style}, color={memory.preferences.font_color}, signature="{memory.preferences.signature}":
    #                     Body Example:
    #                     <p style="font-family: {memory.preferences.font_style}; color: {memory.preferences.font_color};">
    #                     Here is the integration result you requested:<br><br>
    #                     {perceived.expression} = [calculated_result]<br><br>
    #                     {memory.preferences.signature}
    #                     </p>

    #                     OUTPUT FORMAT (JSON only):
    #                     {{
    #                     "action_type": "tool_call" | "final_answer" | "error",
    #                     "tool_call": {{
    #                         "tool_name": "<name>",
    #                         "arguments": {{<args>}},
    #                         "reasoning": "<why this tool>"
    #                     }},
    #                     "reasoning_steps": ["step1", "step2"],
    #                     "should_continue": true/false
    #                     }}

    #                     OR for final answer:
    #                     {{
    #                     "action_type": "final_answer",
    #                     "final_answer": "[LaTeX expression + C]",
    #                     "reasoning_steps": ["summary"],
    #                     "should_continue": false
    #                     }}
    #                     """

    #     return f"""{user_prefs}
    #                 {problem_context}
    #                 {session_context}
    #                 {integrated_terms_context}
    #                 {tool_context}
    #                 {workflow_guidance}

    #                 Now, based on ALL context above (especially personalization preferences), decide the NEXT SINGLE ACTION.
    #                 Respond ONLY in JSON format:
    #             """
    
    async def decide(
        self,
        perceived: PerceivedQuery,
        memory: MemoryContext,
        tool_result: Optional[str] = None
    ) -> DecisionOutput:
        """
        Make decision about next action
        """
        prompt = self._build_decision_prompt(perceived, memory, tool_result)

        try:
            # Run model inference asynchronously
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                ),
                timeout=30
            )

            result_text = response.text.strip()

            # --- Clean JSON ---
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()

            parsed = json.loads(result_text)

            # --- Construct DecisionOutput ---
            if parsed.get("action_type") == "tool_call":
                return DecisionOutput(
                    action_type="tool_call",
                    tool_call=ToolCall(**parsed["tool_call"]),
                    reasoning_steps=parsed.get("reasoning_steps", []),
                    should_continue=parsed.get("should_continue", True)
                )
            elif parsed.get("action_type") == "final_answer":
                return DecisionOutput(
                    action_type="final_answer",
                    final_answer=parsed.get("final_answer"),
                    reasoning_steps=parsed.get("reasoning_steps", []),
                    should_continue=False
                )
            else:
                return DecisionOutput(
                    action_type="error",
                    error_message="Unknown action type",
                    should_continue=False
                )

        except asyncio.TimeoutError:
            return DecisionOutput(
                action_type="error",
                error_message="Decision timeout",
                should_continue=False
            )
        except Exception as e:
            return DecisionOutput(
                action_type="error",
                error_message=f"Decision error: {str(e)}",
                should_continue=False
            )

### NEW ADDITIONS

    async def draft_email_content(
        self,
        perceived: PerceivedQuery,
        memory: MemoryContext,
        final_answer: str
    ) -> dict:
        """
        Use LLM to draft email subject and body based on user instructions
        
        Args:
            perceived: Contains email_instruction with user requirements
            memory: User preferences and session history
            final_answer: The computed integration result
            
        Returns:
            dict with 'subject' and 'body' keys
        """
        
        # Extract email instructions
        email_inst = perceived.email_instruction
        if not email_inst:
            return {
                "subject": f"Answer to the integral of {perceived.expression}",
                "body": f"The result is: {final_answer}"
            }
        
        # Get session steps for context
        steps_summary = []
        for entry in memory.session.history:
            tool = entry.get("tool", "")
            result = entry.get("result", {})
            if tool == "parse_polynomial":
                steps_summary.append("Parsed the polynomial expression into individual terms")
            elif tool == "integrate_term":
                coeff = result.get("coeff", "")
                power = result.get("power", "")
                steps_summary.append(f"Integrated term: coefficient={coeff}, power={power}")
            elif tool == "format_polynomial_latex":
                steps_summary.append("Formatted the integrated result as LaTeX notation")
            elif tool == "differentiate_term":
                steps_summary.append("Verified by differentiation")
            elif tool == "compare_polynomials":
                status = result.get("status", "")
                steps_summary.append(f"Verification: {status}")
        
        # Build drafting prompt
        drafting_prompt = f"""
                        You are drafting an email containing a mathematical solution.

                        USER EMAIL INSTRUCTIONS:
                        - Recipient: {email_inst.recipient}
                        - Subject requirement: {email_inst.subject or 'Answer to the integral'}
                        - Body template: {email_inst.body_template or 'Detail the steps and provide the answer'}
                        - Requested signature: {email_inst.signature or memory.preferences.signature}

                        PROBLEM SOLVED:
                        - Expression: {perceived.expression}
                        - Final Answer: {final_answer}

                        STEPS TAKEN:
                        {chr(10).join(f"- {step}" for step in steps_summary)}

                        USER PREFERENCES:
                        - Math Level: {memory.preferences.math_level}
                        - Explanation Style: {memory.preferences.preferred_explanation_style}
                        - Communication Tone: {memory.preferences.communication_tone}

                        TASK:
                        Draft a professional email following the user's instructions exactly.

                        1. **Subject Line**: 
                        - Follow the user's subject requirement exactly
                        - If they specified a format like "Answer to the integral of <problem> is...", use that format
                        - Fill in the actual problem expression

                        2. **Email Body**:
                        - Start with a brief greeting appropriate for the tone ({memory.preferences.communication_tone})
                        - Detail the steps taken to solve the problem (one paragraph or bullet points based on explanation style)
                        - Present the final answer clearly
                        - Mark where the final answer should appear with: {{{{FINAL_ANSWER}}}}
                        - Do NOT include the signature in the body (it will be added separately)

                        3. **Formatting Notes**:
                        - Use simple HTML tags: <p>, <br>, <strong>, <em>
                        - The final answer will be styled in serif font automatically
                        - Keep language clear and appropriate for {memory.preferences.math_level} level

                        OUTPUT FORMAT (JSON):
                        {{
                            "subject": "<exact_subject_line>",
                            "body": "<html_formatted_body_with_{{{{FINAL_ANSWER}}}}_placeholder>"
                        }}

                        CRITICAL: Respond ONLY with valid JSON.
                        """

        try:
            # Call LLM to draft email
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=drafting_prompt
                    )
                ),
                timeout=30
            )
            
            result_text = response.text.strip()
            
            # Clean JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
            
            drafted = json.loads(result_text)
            
            # Replace placeholder with styled final answer
            body = drafted.get("body", "")
            styled_answer = f'<span style="font-family: serif; font-size: 18px; font-weight: bold;">{final_answer}</span>'
            body = body.replace("{{FINAL_ANSWER}}", styled_answer)
            body = body.replace("{{{{FINAL_ANSWER}}}}", styled_answer)
            
            return {
                "subject": drafted.get("subject", f"Answer to {perceived.expression}"),
                "body": body
            }
            
        except Exception as e:
            # Fallback if LLM fails
            return {
                "subject": f"Answer to the integral of {perceived.expression}",
                "body": f"""
                <p>Here are the steps to solve the integral:</p>
                <ol>
                    {''.join(f'<li>{step}</li>' for step in steps_summary)}
                </ol>
                <p style="font-family: serif; font-size: 18px; font-weight: bold;">
                Final Answer: {final_answer}
                </p>
                """
            }

