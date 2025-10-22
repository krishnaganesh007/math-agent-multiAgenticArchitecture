"""
Action Layer: Contains tool definitions and executes them
Deterministic: Direct tool execution without LLM involvement
"""

from pydantic import BaseModel, Field
from typing import Any, Optional, Literal
from decision import ToolCall
import json
import re
from fractions import Fraction


# Pydantic Models
class ActionResult(BaseModel):
    """Result of action execution"""
    success: bool = Field(description="Whether action succeeded")
    result: Any = Field(description="Tool execution result")
    error_message: Optional[str] = None
    tool_name: str = Field(description="Name of tool executed")


class ActionLayer:
    """Action cognitive layer - contains and executes tools"""
    
    def __init__(self):
        """Initialize action layer with tool registry"""
        self.tools = {
            "show_reasoning": self.show_reasoning,
            "parse_polynomial": self.parse_polynomial,
            "integrate_term": self.integrate_term,
            "differentiate_term": self.differentiate_term,
            "format_polynomial_latex": self.format_polynomial_latex,
            "compare_polynomials": self.compare_polynomials,
            "integrate_symbolic": self.integrate_symbolic,
            "differentiate_symbolic": self.differentiate_symbolic,
            "verify_symbolic_integration": self.verify_symbolic_integration,
        }
    
    # ========================================================================
    # TOOL IMPLEMENTATIONS
    # ========================================================================
    
    def show_reasoning(self, steps: list) -> dict:
        """Show step-by-step reasoning process"""
        print("\n[REASONING]")
        for i, step in enumerate(steps, 1):
            print(f"  Step {i}: {step}")
        return {"status": "success", "message": "Reasoning displayed"}
    
    def parse_polynomial(self, expression: str) -> dict:
        """Parse a polynomial expression into structured terms"""
        print(f"\n[TOOL] parse_polynomial({expression})")
        
        # Clean the expression
        expr = expression.replace(" ", "").replace("dx", "").replace("∫", "")
        
        # Better regex that handles constants properly
        pattern = r'([+-]?)(\d+\.?\d*)(x?)(\^?)(\d*\.?\d*)'
        matches = re.findall(pattern, expr)
        
        terms = []
        for match in matches:
            sign, coeff, has_x, has_caret, power_str = match
            
            # Skip empty matches
            if not coeff:
                continue
            
            # Parse coefficient
            coeff_val = float(coeff)
            if sign == '-':
                coeff_val = -coeff_val
            
            # Determine power
            if not has_x:  # Constant term (no x)
                power = 0.0
            elif has_caret and power_str:  # x^n
                power = float(power_str)
            elif has_x:  # Just x (means x^1)
                power = 1.0
            else:
                power = 0.0
            
            terms.append({"coeff": coeff_val, "power": power})
        
        print(f"  → Parsed: {terms}")
        return {"status": "success", "terms": terms}
    
    def integrate_term(self, coeff: float, power: float) -> dict:
        """Apply power rule to integrate a single term"""
        print(f"\n[TOOL] integrate_term({coeff}, {power})")
        
        if power == -1:
            return {"status": "error", "message": "logarithmic_case"}
        else:
            new_power = power + 1
            new_coeff = coeff / new_power
            result = {"status": "success", "coeff": new_coeff, "power": new_power}
            print(f"  → Result: {new_coeff}x^{new_power}")
            return result
    
    def differentiate_term(self, coeff: float, power: float) -> dict:
        """Apply power rule to differentiate a term"""
        print(f"\n[TOOL] differentiate_term({coeff}, {power})")
        
        if power == 0:
            result = {"status": "zero", "coeff": 0.0, "power": 0.0}
        else:
            new_coeff = coeff * power
            new_power = power - 1
            result = {"status": "success", "coeff": new_coeff, "power": new_power}
        
        print(f"  → Derivative: {result}")
        return result
    
    def format_polynomial_latex(self, terms: list) -> dict:
        """Convert polynomial terms to LaTeX string"""
        print(f"\n[TOOL] format_polynomial_latex()")
        
        latex_parts = []
        for i, term in enumerate(terms):
            coeff = term['coeff']
            power = term['power']
            
            if abs(coeff) < 1e-10:
                continue
            
            abs_coeff = abs(coeff)
            sign_str = "-" if coeff < 0 else ("" if i == 0 else " + ")
            if i > 0 and coeff < 0:
                sign_str = " - "
            
            if power == 0:
                latex_parts.append(f"{sign_str}{abs_coeff:.4g}")
            elif power == 1:
                if abs_coeff == 1:
                    latex_parts.append(f"{sign_str}x")
                else:
                    latex_parts.append(f"{sign_str}{abs_coeff:.4g}x")
            else:
                frac = Fraction(coeff).limit_denominator(20)
                if frac.denominator != 1 and abs(frac.numerator) <= 10:
                    num = abs(frac.numerator)
                    denom = frac.denominator
                    latex_parts.append(f"{sign_str}\\frac{{{num}x^{{{int(power)}}}}}{{{denom}}}")
                else:
                    latex_parts.append(f"{sign_str}{abs_coeff:.4g}x^{{{int(power)}}}")
        
        result = "".join(latex_parts) + " + C"
        print(f"  → LaTeX: {result}")
        return {"status": "success", "latex": result}
    
    def compare_polynomials(self, original_terms: list, verified_terms: list) -> dict:
        """Compare two polynomial term lists for equality"""
        print(f"\n[TOOL] compare_polynomials()")
        
        def normalize(terms):
            normalized = {}
            for t in terms:
                power = round(t['power'], 6)
                coeff = round(t['coeff'], 6)
                normalized[power] = normalized.get(power, 0) + coeff
            return normalized
        
        orig_norm = normalize(original_terms)
        verif_norm = normalize(verified_terms)
        
        if orig_norm == verif_norm:
            result = {"status": "pass", "message": "Verification successful"}
            print("  → ✓ VERIFIED")
        else:
            discrepancies = []
            all_powers = set(orig_norm.keys()) | set(verif_norm.keys())
            for p in sorted(all_powers, reverse=True):
                orig_c = orig_norm.get(p, 0)
                verif_c = verif_norm.get(p, 0)
                if abs(orig_c - verif_c) > 1e-9:
                    discrepancies.append({"power": p, "expected": orig_c, "got": verif_c})
            result = {"status": "fail", "message": "Verification failed", "discrepancies": discrepancies}
            print("  → ✗ FAILED")
        
        return result
    
    def integrate_symbolic(self, expression: str, variable: str = "x") -> dict:
        """Integrate any expression using SymPy"""
        print(f"\n[TOOL] integrate_symbolic({expression}, {variable})")
        
        try:
            import sympy as sp
            var = sp.Symbol(variable)
            expr_str = expression.replace("^", "**")
            expr = sp.sympify(expr_str)
            antiderivative = sp.integrate(expr, var)
            
            result = {
                "status": "success",
                "antiderivative": str(antiderivative),
                "latex": sp.latex(antiderivative) + " + C",
                "simplified": str(sp.simplify(antiderivative))
            }
            print(f"  → Result: {result['latex']}")
            return result
        except ImportError:
            return {"status": "error", "message": "SymPy not installed. Run: pip install sympy"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def differentiate_symbolic(self, expression: str, variable: str = "x") -> dict:
        """Differentiate expression using SymPy"""
        print(f"\n[TOOL] differentiate_symbolic({expression}, {variable})")
        
        try:
            import sympy as sp
            var = sp.Symbol(variable)
            expr = sp.sympify(expression.replace("^", "**"))
            derivative = sp.diff(expr, var)
            
            result = {
                "status": "success",
                "derivative": str(derivative),
                "latex": sp.latex(derivative),
                "simplified": str(sp.simplify(derivative))
            }
            print(f"  → Derivative: {result['latex']}")
            return result
        except ImportError:
            return {"status": "error", "message": "SymPy not installed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def verify_symbolic_integration(self, original: str, antiderivative: str, variable: str = "x") -> dict:
        """Verify integration by differentiating"""
        print(f"\n[TOOL] verify_symbolic_integration()")
        
        try:
            import sympy as sp
            var = sp.Symbol(variable)
            orig_expr = sp.sympify(original.replace("^", "**"))
            anti_expr = sp.sympify(antiderivative.replace("^", "**"))
            derivative = sp.diff(anti_expr, var)
            difference = sp.simplify(derivative - orig_expr)
            is_equal = difference == 0
            
            result = {
                "status": "pass" if is_equal else "fail",
                "match": is_equal,
                "message": "Verification successful" if is_equal else "Mismatch detected"
            }
            print("  → ✓ VERIFIED" if is_equal else "  → ✗ FAILED")
            return result
        except ImportError:
            return {"status": "error", "message": "SymPy not installed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # ========================================================================
    # EXECUTION METHOD
    # ========================================================================
    
    def execute(self, tool_call: ToolCall) -> ActionResult:
        """
        Execute a tool call
        
        Args:
            tool_call: ToolCall decision from decision layer
            
        Returns:
            ActionResult with execution outcome
        """
        tool_name = tool_call.tool_name
        
        # Check if tool exists
        if tool_name not in self.tools:
            return ActionResult(
                success=False,
                result=None,
                error_message=f"Unknown tool: {tool_name}",
                tool_name=tool_name
            )
        
        try:
            # Get the tool function
            tool_func = self.tools[tool_name]
            
            # Execute the tool with arguments
            result = tool_func(**tool_call.arguments)
            
            return ActionResult(
                success=True,
                result=result,
                tool_name=tool_name
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                result=None,
                error_message=f"Tool execution error: {str(e)}",
                tool_name=tool_name
            )
    
    def format_result_for_decision(self, action_result: ActionResult) -> str:
        """Format action result for passing back to decision layer"""
        if action_result.success:
            return f"Tool '{action_result.tool_name}' succeeded: {json.dumps(action_result.result, indent=2)}"
        else:
            return f"Tool '{action_result.tool_name}' failed: {action_result.error_message}"
