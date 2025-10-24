# """
# Decision Layer: Plans the execution strategy based on perception and memory
# Non-Deterministic: Uses LLM for planning and decision-making
# """

# from pydantic import BaseModel, Field
# from typing import Literal, Optional, Any
# from perception import PerceivedQuery
# from memory import MemoryContext
# from google import genai
# import asyncio
# import json
# import os
# from dotenv import load_dotenv

# # Load environment
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")
# client = genai.Client(api_key=api_key)


# # Pydantic Models
# class ToolCall(BaseModel):
#     """Represents a single tool call decision"""
#     tool_name: str = Field(description="Name of tool to call")
#     arguments: dict[str, Any] = Field(description="Arguments for the tool")
#     reasoning: str = Field(description="Why this tool is being called")


# class DecisionOutput(BaseModel):
#     """Output from decision layer"""
#     action_type: Literal["tool_call", "final_answer", "error"] = Field(
#         description="Type of action to take"
#     )
#     tool_call: Optional[ToolCall] = None
#     final_answer: Optional[str] = None
#     error_message: Optional[str] = None
#     reasoning_steps: list[str] = Field(default_factory=list)
#     should_continue: bool = Field(default=True, description="Whether to continue loop")


# class DecisionLayer:
#     """Decision cognitive layer - plans execution strategy"""
    
#     def __init__(self):
#         self.client = client
#         self.conversation_history = []
    
#     def _build_decision_prompt(
#         self,
#         perceived: PerceivedQuery,
#         memory: MemoryContext,
#         tool_result: Optional[str] = None
#     ) -> str:
#         """Build prompt for decision-making LLM"""
        
#         user_prefs = f"""
# USER PREFERENCES (from memory):
# - Name: {memory.preferences.name}
# - Explanation Style: {memory.preferences.preferred_explanation_style}
# - Preferred Method: {memory.preferences.preferred_method}
# - Math Level: {memory.preferences.math_level}
# - Show Reasoning: {memory.preferences.show_reasoning}
# - Verification Required: {memory.preferences.verification_required}
# """
        
#         problem_context = f"""
# PERCEIVED PROBLEM:
# - Type: {perceived.problem_type}
# - Expression: {perceived.expression}
# - Variable: {perceived.variable}
# - Features: {json.dumps(perceived.key_features)}
# """
        
#         session_context = f"""
# SESSION STATE:
# - Iteration: {memory.session.iteration_count}
# - Parsed Terms: {memory.session.parsed_terms}
# - Integrated Terms Count: {len(memory.session.integrated_terms)}
# - Differentiated Terms Count: {len(memory.session.differentiated_terms)}
# """
        
#         tool_context = f"\nLAST TOOL RESULT:\n{tool_result}\n" if tool_result else ""
        
#         workflow_guidance = """
# AVAILABLE TOOLS:
# 1. show_reasoning(steps: list) - Display reasoning
# 2. parse_polynomial(expression: str) - Parse polynomial
# 3. integrate_term(coeff: float, power: float) - Integrate single term
# 4. differentiate_term(coeff: float, power: float) - Differentiate term
# 5. format_polynomial_latex(terms: list) - Format as LaTeX
# 6. compare_polynomials(original: list, verified: list) - Verify
# 7. integrate_symbolic(expression: str, variable: str) - Symbolic integration
# 8. differentiate_symbolic(expression: str, variable: str) - Symbolic differentiation
# 9. verify_symbolic_integration(original: str, antiderivative: str, variable: str) - Verify symbolic

# DECISION RULES:
# - For POLYNOMIAL problems: Use parse_polynomial → integrate_term (each) → format → verify workflow
# - For SYMBOLIC problems: Use integrate_symbolic → differentiate_symbolic → verify workflow
# - ALWAYS incorporate user preferences (explanation style, method preference)
# - If user prefers manual and problem is polynomial, use polynomial workflow
# - If user prefers symbolic, use symbolic workflow
# - If verification_required=True, always verify before final answer

# OUTPUT FORMAT (JSON only):
# {
#     "action_type": "tool_call" | "final_answer" | "error",
#     "tool_call": {
#         "tool_name": "<name>",
#         "arguments": {<args>},
#         "reasoning": "<why this tool>"
#     },
#     "reasoning_steps": ["step1", "step2"],
#     "should_continue": true/false
# }

# OR for final answer:
# {
#     "action_type": "final_answer",
#     "final_answer": "[LaTeX expression + C]",
#     "reasoning_steps": ["summary"],
#     "should_continue": false
# }
# """
        
#         return f"""{user_prefs}
# {problem_context}
# {session_context}
# {tool_context}
# {workflow_guidance}

# Based on ALL context above (especially user preferences), decide the NEXT SINGLE action.
# Respond with JSON only:"""
    
#     async def decide(
#         self,
#         perceived: PerceivedQuery,
#         memory: MemoryContext,
#         tool_result: Optional[str] = None
#     ) -> DecisionOutput:
#         """
#         Make decision about next action
        
#         Args:
#             perceived: Structured query from perception
#             memory: User preferences and session state
#             tool_result: Result from last tool execution (if any)
            
#         Returns:
#             DecisionOutput with next action to take
#         """
#         prompt = self._build_decision_prompt(perceived, memory, tool_result)
        
#         try:
#             # Run model inference asynchronously
#             loop = asyncio.get_event_loop()
#             response = await asyncio.wait_for(
#                 loop.run_in_executor(
#                     None,
#                     lambda: self.client.models.generate_content(
#                         model="gemini-2.5-flash",
#                         contents=prompt
#                     )
#                 ),
#                 timeout=30
#             )
            
#             result_text = response.text.strip()

#             # --- Clean JSON ---
#             if "```json" in result_text:
#                 result_text = result_text.split("```json")[1].split("```")[0].strip()
#             elif "```" in result_text:
#                 result_text = result_text.split("```")[1].strip()

#             parsed = json.loads(result_text)
            
#             # --- Construct DecisionOutput ---
#             if parsed.get("action_type") == "tool_call":
#                 return DecisionOutput(
#                     action_type="tool_call",
#                     tool_call=ToolCall(**parsed["tool_call"]),
#                     reasoning_steps=parsed.get("reasoning_steps", []),
#                     should_continue=parsed.get("should_continue", True)
#                 )
#             elif parsed.get("action_type") == "final_answer":
#                 return DecisionOutput(
#                     action_type="final_answer",
#                     final_answer=parsed.get("final_answer"),
#                     reasoning_steps=parsed.get("reasoning_steps", []),
#                     should_continue=False
#                 )
#             else:
#                 return DecisionOutput(
#                     action_type="error",
#                     error_message="Unknown action type",
#                     should_continue=False
#                 )
                
#         except asyncio.TimeoutError:
#             return DecisionOutput(
#                 action_type="error",
#                 error_message="Decision timeout",
#                 should_continue=False
#             )
#         except Exception as e:
#             return DecisionOutput(
#                 action_type="error",
#                 error_message=f"Decision error: {str(e)}",
#                 should_continue=False
#             )


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
        """Build prompt for decision-making LLM"""

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
        
        # --- NEW: Already integrated terms context ---
        integrated_terms_context = ""
        if memory.session.integrated_terms:
            integrated_terms_context = f"""
                ALREADY INTEGRATED TERMS:
                {memory.session.integrated_terms}
                Ensure that these terms are NOT integrated again.
            """

        tool_context = f"\nLAST TOOL RESULT:\n{tool_result}\n" if tool_result else ""

        # --- TOOL CONTEXT ---
        workflow_guidance = """
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
                            10. send_gmail_text_personalized(to: str,subject: str,body: str,font_style: str = "Arial",font_color: str = "black",signature: str = "",tone: str = "friendly",sender: str = "me")— Send an email message.

                            DECISION RULES:
                            - Use polynomial or symbolic workflows depending on problem type and user preference.
                            - Respect user explanation style, method, and math level.
                            - If verification_required=True, verify before final answer.
                            - If task involves communication (e.g., sending an email or summarizing results):
                            - Use user’s font style and font color for formatting.
                            - Match the user’s communication tone:
                                • "friendly" → use warm and conversational phrasing
                                • "professional" → use formal and polite language
                                • "casual" → keep short and relaxed
                            - Always include user’s signature at the end.
                            - Format the email body as an HTML or styled plain text message.
                            - Prefer `send_gmail_text_personalized` tool for sending such messages.

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
                            "reasoning": "<why this tool>"
                        }},
                        "reasoning_steps": ["step1", "step2"],
                        "should_continue": true/false
                        }}

                        OR for final answer:
                        {{
                        "action_type": "final_answer",
                        "final_answer": "[LaTeX expression + C]",
                        "reasoning_steps": ["summary"],
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
