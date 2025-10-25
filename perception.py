# """
# Perception Layer: Translates raw user queries into structured information
# Non-Deterministic: Uses LLM to extract intent and classify problem type
# """

# from pydantic import BaseModel, Field
# from typing import Literal
# from google import genai
# import asyncio
# import os
# import json
# from dotenv import load_dotenv

# # Load environment
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")
# client = genai.Client(api_key=api_key)


# # Pydantic Models
# class PerceivedQuery(BaseModel):
#     """Structured output from perception layer"""
#     original_query: str = Field(description="Original user query")
#     problem_type: Literal["polynomial", "symbolic", "unknown"] = Field(
#         description="Type of mathematical problem identified"
#     )
#     expression: str = Field(description="Extracted mathematical expression")
#     variable: str = Field(default="x", description="Variable of integration")
#     reasoning: list[str] = Field(
#         default_factory=list,
#         description="Step-by-step classification reasoning"
#     )
#     key_features: dict = Field(
#         default_factory=dict,
#         description="Detected features (e.g., has_trig, has_exp, has_log)"
#     )


# class PerceptionLayer:
#     """Perception cognitive layer - interprets and structures user input"""
    
#     def __init__(self):
#         self.client = client
#         self.system_prompt = """
# You are a mathematical problem classifier.

# Your role: Analyze the given integration problem and extract structured information for downstream reasoning tools.

# ---

# CLASSIFICATION RULES:
# 1. POLYNOMIAL → Only x terms with integer or rational powers (e.g., 4x^6 - 2x^3 + 7x - 4)
# 2. SYMBOLIC → Contains trigonometric (sin, cos, tan, csc, sec, cot), exponential (exp), or logarithmic (log) functions
# 3. UNKNOWN → Cannot confidently determine problem type (e.g., multiple variables, invalid syntax)

# ---

# SELF-CHECK RULES:
# - Detect and verify the main variable (x, t, y, etc.)
# - Cross-check detected features for consistency:
#   * If has_trig / has_exp / has_log = true → problem_type must be "symbolic"
#   * If only polynomial terms detected → problem_type must be "polynomial"
# - If ambiguous or conflicting signals → classify as "unknown"
# - Always provide a numeric confidence score between 0 and 1
# - If parsing fails or confidence < 0.5 → include fallback_reason

# ---

# OUTPUT FORMAT (STRICT JSON):
# Respond ONLY with valid JSON (no markdown, no text before or after).

# {
#     "problem_type": "polynomial" | "symbolic" | "unknown",
#     "expression": "<cleaned_expression>",
#     "variable": "<variable_letter_or_null>",
#     "reasoning": [
#         "[CLASSIFICATION] Identified main variable.",
#         "[PATTERN_MATCH] Found polynomial powers only.",
#         "[DECISION] Classified as polynomial."
#     ],
#     "key_features": {
#         "has_trig": true/false,
#         "has_exp": true/false,
#         "has_log": true/false,
#         "has_polynomials": true/false,
#         "max_power": <number_or_null>
#     },
#     "confidence": <float_between_0_and_1>,
#     "fallback_reason": "<reason_if_unknown_or_uncertain_else_null>"
# }

# ---

# CRITICAL INSTRUCTIONS:
# - Respond only with valid JSON.
# - Include reasoning steps explaining how the classification was reached.
# - If uncertain, clearly explain the fallback_reason.
# - No extra commentary or markdown formatting.
# """

    
#     async def perceive(self, user_query: str) -> PerceivedQuery:
#         """
#         Transform raw query into structured perception
        
#         Args:
#             user_query: Raw user input (e.g., "∫4x^6 - 2x^3 + 7x - 4 dx")
            
#         Returns:
#             PerceivedQuery with structured information
#         """
#         prompt = f"""{self.system_prompt}

# USER QUERY: {user_query}

# Analyze and respond with JSON only:"""
        
#         try:
#             # Call LLM asynchronously
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
            
#             # Parse LLM response
#             result_text = response.text.strip()

#             # --- Clean JSON text ---
#             if "```json" in result_text:
#                 result_text = result_text.split("```json")[1].split("```")[0].strip()
#             elif "```" in result_text:
#                 result_text = result_text.split("```")[1].strip()

#             # Parse to dict
#             parsed = json.loads(result_text)
            
#             # Construct PerceivedQuery object
#             perceived = PerceivedQuery(
#                 original_query=user_query,
#                 problem_type=parsed.get("problem_type", "unknown"),
#                 expression=parsed.get("expression", user_query),
#                 variable=parsed.get("variable", "x"),
#                 reasoning=parsed.get("reasoning", []),
#                 key_features=parsed.get("key_features", {})
#             )
            
#             return perceived
            
#         except asyncio.TimeoutError:
#             return PerceivedQuery(
#                 original_query=user_query,
#                 problem_type="unknown",
#                 expression=user_query,
#                 variable="x",
#                 reasoning=["[ERROR] LLM timeout - using fallback"],
#                 key_features={}
#             )
#         except Exception as e:
#             return PerceivedQuery(
#                 original_query=user_query,
#                 problem_type="unknown",
#                 expression=user_query,
#                 variable="x",
#                 reasoning=[f"[ERROR] {str(e)}"],
#                 key_features={}
#             )




### New functionality

"""
Perception Layer: Translates raw user queries into structured information
Non-Deterministic: Uses LLM to extract intent and classify problem type
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional, Dict, Any
from google import genai
import asyncio
import os
import json
from dotenv import load_dotenv
import re

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


# ----------------------------------------------------------------------------
# Pydantic Models
# ----------------------------------------------------------------------------

class EmailInstruction(BaseModel):
    """Email instructions extracted from user query"""
    recipient: EmailStr
    subject: Optional[str] = None
    body_template: Optional[str] = None
    signature: Optional[str] = None
    font_color: Optional[str] = None
    font_style: Optional[str] = None


class PerceivedQuery(BaseModel):
    """Structured output from perception layer"""
    original_query: str = Field(description="Original user query")
    problem_type: Literal["polynomial", "symbolic", "unknown"] = Field(
        description="Type of mathematical problem identified"
    )
    expression: str = Field(description="Extracted mathematical expression")
    variable: str = Field(default="x", description="Variable of integration")
    reasoning: list[str] = Field(
        default_factory=list,
        description="Step-by-step classification reasoning"
    )
    key_features: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detected features (e.g., has_trig, has_exp, has_log)"
    )
    email_instruction: Optional[EmailInstruction] = None


# ----------------------------------------------------------------------------
# Perception Layer
# ----------------------------------------------------------------------------

class PerceptionLayer:
    """Perception cognitive layer - interprets and structures user input"""
    
    def __init__(self):
        self.client = client
        # self.system_prompt = """
        #                         You are a mathematical problem classifier and email intent recognizer.

        #                         ROLE:
        #                         1. Extract structured mathematical problem details.
        #                         2. Detect if the user intends to send the result via email, and extract recipient, subject, and optional body/style preferences.

        #                         CLASSIFICATION RULES:
        #                         - POLYNOMIAL → Only x terms with integer or rational powers (e.g., 4x^6 - 2x^3 + 7x - 4)
        #                         - SYMBOLIC → Contains trigonometric, exponential, or logarithmic functions
        #                         - UNKNOWN → Cannot confidently determine problem type

        #                         EMAIL RULES:
        #                         - Detect email addresses and phrases like "send the answer to ..."
        #                         - Optionally detect desired tone, signature, font color, or style

        #                         OUTPUT FORMAT (STRICT JSON):
        #                         {
        #                         "problem_type": "polynomial" | "symbolic" | "unknown",
        #                         "expression": "<cleaned_expression>",
        #                         "variable": "<variable_letter_or_null>",
        #                         "reasoning": ["[CLASSIFICATION] ...", "[EMAIL] ..."],
        #                         "key_features": {
        #                             "has_trig": true/false,
        #                             "has_exp": true/false,
        #                             "has_log": true/false,
        #                             "has_polynomials": true/false,
        #                             "max_power": <number_or_null>
        #                         },
        #                         "confidence": <float_between_0_and_1>,
        #                         "fallback_reason": "<reason_if_unknown_or_uncertain_else_null>",
        #                         "email_instruction": {
        #                             "recipient": "<email_or_null>",
        #                             "subject": "<optional_subject>",
        #                             "body_template": "<optional_body_template>",
        #                             "signature": "<optional_signature>",
        #                             "font_color": "<optional_color>",
        #                             "font_style": "<optional_style>"
        #                         }
        #                         }

        #                         CRITICAL:
        #                         - Respond only with valid JSON.
        #                         - Include reasoning steps for math classification and email detection.
        #                         - If unsure, provide fallback_reason or nulls.
        #                         """
        self.system_prompt = """
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
                                    }"""

    async def perceive(self, user_query: str) -> PerceivedQuery:
        """
        Transform raw query into structured perception
        
        Args:
            user_query: Raw user input (e.g., "∫4x^6 - 2x^3 + 7x - 4 dx and send to test@example.com")
            
        Returns:
            PerceivedQuery with structured information
        """
        # Quick regex-based email detection fallback
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', user_query)
        email_inst = None
        if email_match:
            email_inst = EmailInstruction(recipient=email_match.group(0))

        # Prepare prompt for LLM
        prompt = f"""{self.system_prompt}

USER QUERY: {user_query}

Analyze and respond with JSON only:"""
        
        try:
            # Call LLM asynchronously
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
            
            # Clean LLM response
            result_text = response.text.strip()
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()

            parsed = json.loads(result_text)

            # Ensure email_instruction exists
            if not parsed.get("email_instruction") and email_inst:
                parsed["email_instruction"] = email_inst.model_dump()

            perceived = PerceivedQuery(
                original_query=user_query,
                problem_type=parsed.get("problem_type", "unknown"),
                expression=parsed.get("expression", user_query),
                variable=parsed.get("variable", "x"),
                reasoning=parsed.get("reasoning", []),
                key_features=parsed.get("key_features", {}),
                email_instruction=parsed.get("email_instruction")
            )
            
            return perceived

        except asyncio.TimeoutError:
            return PerceivedQuery(
                original_query=user_query,
                problem_type="unknown",
                expression=user_query,
                variable="x",
                reasoning=["[ERROR] LLM timeout - using fallback"],
                key_features={},
                email_instruction=email_inst.model_dump() if email_inst else None
            )
        except Exception as e:
            return PerceivedQuery(
                original_query=user_query,
                problem_type="unknown",
                expression=user_query,
                variable="x",
                reasoning=[f"[ERROR] {str(e)}"],
                key_features={},
                email_instruction=email_inst.model_dump() if email_inst else None
            )
