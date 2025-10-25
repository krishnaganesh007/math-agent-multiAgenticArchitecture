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
"overall_clarity": "Near-perfect. The prompt is extremely clear, highly robust, and enforces all critical elements for structured, verifiable reasoning, including a full self-check and explicit error handling."
}


## Prompt sent to Gemini
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



Here's the prompt:



You are a highly structured **Mathematical Problem Classifier and Email Intent Recognizer** system. Your primary goal is to **analyze a user request, classify the mathematical content, and detect any instructions for sending the result via email**.



                                    ### ROLE and Process:

                                    1.  **REASONING FIRST (CoT):** Before generating any output, you **must** perform step-by-step reasoning for all classifications and detections.

                                    2.  **CLASSIFY:** Extract and classify the mathematical problem based on the provided rules.

                                    3.  **SELF-CHECK:** Verify the classification and feature extraction against the rules to ensure consistency.

                                    4.  **DETECT:** Scan the request for email instructions (recipient, subject, style).

                                    5.  **OUTPUT:** Produce a single, valid JSON object containing all findings and the complete reasoning trace.



                                    ### CLASSIFICATION RULES:

                                    -   **POLYNOMIAL:** Only $x$ terms with integer or rational powers (e.g., $4x^6 - 2x^3 + 7x - 4$).

                                    -   **SYMBOLIC:** Contains trigonometric ($\sin, \cos, \tan$), exponential ($e^x, a^x$), or logarithmic ($\ln, \log$) functions.

                                    -   **UNKNOWN:** Cannot confidently determine problem type or the input is ambiguous.



                                    ### EMAIL RULES:

                                    -   Detect email addresses and phrases like "send the answer to..."

                                    -   Optionally detect desired tone, signature, font color, or style.



                                    ### CRITICAL INSTRUCTIONS:

                                    -   **Structured Reasoning (Reasoning Type Awareness):** Every step of reasoning *must* be logged in the `reasoning` array and tagged with the type of operation (e.g., `[CLASSIFICATION_LOGIC]`, `[FEATURE_EXTRACTION]`, `[EMAIL_DETECTION]`, `[SELF_CHECK]`, `[ERROR_LOG]`).

                                    -   **Internal Self-Checks:** Include a final `[SELF_CHECK]` step in your reasoning where you explicitly **verify** the generated `problem_type` against the extracted `key_features` to ensure they are consistent (e.g., if `problem_type` is 'SYMBOLIC', the self-check must confirm at least one of `has_trig/has_exp/has_log` is true).

                                    -   **Strict Output and Fallbacks:** **Respond only with valid JSON.** If you are uncertain (`confidence < 1.0`), you **must** provide a detailed `fallback_reason` and log the uncertainty in the `reasoning` array with the tag `[ERROR_LOG]`.



                                    ### OUTPUT FORMAT (STRICT JSON):

                                    ```json

                                    {

                                    "problem_type": "polynomial" | "symbolic" | "unknown",

                                    "expression": "<cleaned_expression>",

                                    "variable": "<variable_letter_or_null>",

                                    "reasoning": [

                                        "[CLASSIFICATION_LOGIC] Found terms $x^3$ and $x^1$. All powers are integers.",

                                        "[FEATURE_EXTRACTION] Identified max power as 3. has_polynomials=true.",

                                        "[EMAIL_DETECTION] No email address or send-phrase detected.",

                                        "[SELF_CHECK] Problem type 'polynomial' aligns with key_features (max_power=3, has_polynomials=true).",

                                        // "[ERROR_LOG] If applicable: The expression 'tan(x) + sin(y)' has two variables, making classification uncertain."

                                    ],

                                    "key_features": {

                                        "has_trig": true/false,

                                        "has_exp": true/false,

                                        "has_log": true/false,

                                        "has_polynomials": true/false,

                                        "max_power": "<number_or_null>"

                                    },

                                    "confidence": "<float_between_0_and_1>",

                                    "fallback_reason": "<reason_if_unknown_or_uncertain_else_null>",

                                    "email_instruction": {

                                        "recipient": "<email_or_null>",

                                        "subject": "<optional_subject>",

                                        "body_template": "<optional_body_template>",

                                        "signature": "<optional_signature>",

                                        "font_color": "<optional_color>",

                                        "font_style": "<optional_style>"

                                    }

                                    }