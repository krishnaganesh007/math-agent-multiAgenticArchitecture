"""
Perception Layer: Translates raw user queries into structured information
Non-Deterministic: Uses LLM to extract intent and classify problem type
"""

from pydantic import BaseModel, Field
from typing import Literal
from google import genai
import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


# Pydantic Models
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
    key_features: dict = Field(
        default_factory=dict,
        description="Detected features (e.g., has_trig, has_exp, has_log)"
    )


class PerceptionLayer:
    """Perception cognitive layer - interprets and structures user input"""
    
    def __init__(self):
        self.client = client
        self.system_prompt = """You are a mathematical problem classifier.
        
Your task: Analyze the given integration problem and extract structured information.

CLASSIFICATION RULES:
1. POLYNOMIAL: Only x terms with integer/rational powers (e.g., 4x^6 - 2x^3 + 7x - 4)
2. SYMBOLIC: Contains trig (sin, cos, tan, csc, sec, cot), exp, log, or complex functions
3. UNKNOWN: Cannot determine type

OUTPUT FORMAT (JSON):
{
    "problem_type": "polynomial" | "symbolic" | "unknown",
    "expression": "<cleaned expression>",
    "variable": "<variable letter>",
    "reasoning": ["[CLASSIFICATION] step 1", "[ALGEBRA] step 2", ...],
    "key_features": {
        "has_trig": true/false,
        "has_exp": true/false,
        "has_log": true/false,
        "has_polynomials": true/false,
        "max_power": <number or null>
    }
}

CRITICAL: Respond ONLY with valid JSON. No additional text."""
    
    async def perceive(self, user_query: str) -> PerceivedQuery:
        """
        Transform raw query into structured perception
        
        Args:
            user_query: Raw user input (e.g., "∫4x^6 - 2x^3 + 7x - 4 dx")
            
        Returns:
            PerceivedQuery with structured information
        """
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
                        model="gemini-2.0-flash",
                        contents=prompt
                    )
                ),
                timeout=30
            )
            
            # Parse LLM response
            result_text = response.text.strip()

            # --- Clean JSON text ---
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()

            # Parse to dict
            parsed = json.loads(result_text)
            
            # Construct PerceivedQuery object
            perceived = PerceivedQuery(
                original_query=user_query,
                problem_type=parsed.get("problem_type", "unknown"),
                expression=parsed.get("expression", user_query),
                variable=parsed.get("variable", "x"),
                reasoning=parsed.get("reasoning", []),
                key_features=parsed.get("key_features", {})
            )
            
            return perceived
            
        except asyncio.TimeoutError:
            return PerceivedQuery(
                original_query=user_query,
                problem_type="unknown",
                expression=user_query,
                variable="x",
                reasoning=["[ERROR] LLM timeout - using fallback"],
                key_features={}
            )
        except Exception as e:
            return PerceivedQuery(
                original_query=user_query,
                problem_type="unknown",
                expression=user_query,
                variable="x",
                reasoning=[f"[ERROR] {str(e)}"],
                key_features={}
            )
