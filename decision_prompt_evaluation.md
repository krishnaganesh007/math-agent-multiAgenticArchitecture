## Output:
{
"explicit_reasoning": true,
"structured_output": true,
"tool_separation": true,
"conversation_loop": true,
"instructional_framing": true,
"internal_self_checks": true,
"reasoning_type_awareness": true,
"fallbacks": true,
"overall_clarity": "Excellent. This prompt is a model of robustness for a tool-using agent, passing all criteria by leveraging comprehensive context and strictly enforced, actionable JSON output."
}

## Prompt (sent to gemini):
You are a Prompt Evaluation Assistant.
You will receive a prompt written by a student. Your job is to review this prompt
and assess how well it supports structured, step-by-step reasoning in an LLM (e.g.,
for math, logic, planning, or tool use).
Evaluate the prompt on the following criteria:
1. Explicit Reasoning Instructions✅
- Does the prompt tell the model to reason step-by-step?
- Does it include instructions like “explain your thinking” or “think before you
answer”?
2. Structured Output Format✅
- Does the prompt enforce a predictable output format (e.g., FUNCTION_CALL,
JSON, numbered steps)?
- Is the output easy to parse or validate?
3. Separation of Reasoning and Tools✅
- Are reasoning steps clearly separated from computation or tool-use steps?
- Is it clear when to calculate, when to verify, when to reason?
4. Conversation Loop Support✅
- Could this prompt work in a back-and-forth (multi-turn) setting?
- Is there a way to update the context with results from previous steps?
5. Instructional Framing✅
- Are there examples of desired behavior or “formats” to follow?
- Does the prompt define exactly how responses should look?
6. Internal Self-Checks✅
- Does the prompt instruct the model to self-verify or sanity-check intermediate
steps?
7. Reasoning Type Awareness✅
- Does the prompt encourage the model to tag or identify the type of reasoning
used (e.g., arithmetic, logic, lookup)?
8. Error Handling or Fallbacks✅
- Does the prompt specify what to do if an answer is uncertain, a tool fails, or
the model is unsure?
9. Overall Clarity and Robustness✅
- Is the prompt easy to follow?
- Is it likely to reduce hallucination and drift?
---
Respond with a structured review in this format:json
{
"explicit_reasoning": true,
"structured_output": true,
"tool_separation": true,
"conversation_loop": true,
"instructional_framing": true,
"internal_self_checks": false,
"reasoning_type_awareness": false,
"fallbacks": false,
"overall_clarity": "Excellent structure, but could improve with self-checks and
error fallbacks."
}

Here's how the prompt is built:
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

