# """
# Action Layer: Executes tools based on decisions
# Deterministic: Direct tool execution without LLM involvement
# """

# from pydantic import BaseModel, Field
# from typing import Any, Optional
# from mcp import ClientSession
# from decision import ToolCall
# import json


# # Pydantic Models
# class ActionResult(BaseModel):
#     """Result of action execution"""
#     success: bool = Field(description="Whether action succeeded")
#     result: Any = Field(description="Tool execution result")
#     error_message: Optional[str] = None
#     tool_name: str = Field(description="Name of tool executed")


# class ActionLayer:
#     """Action cognitive layer - executes tools"""
    
#     def __init__(self, mcp_session: ClientSession):
#         self.session = mcp_session
    
#     async def execute(self, tool_call: ToolCall) -> ActionResult:
#         """
#         Execute a tool call
        
#         Args:
#             tool_call: ToolCall decision from decision layer
            
#         Returns:
#             ActionResult with execution outcome
#         """
#         try:
#             # Call MCP tool
#             tool_result = await self.session.call_tool(
#                 tool_call.tool_name,
#                 arguments=tool_call.arguments
#             )
            
#             # Extract result
#             if tool_result.content:
#                 result_text = tool_result.content[0].text
                
#                 # Try to parse as JSON if possible
#                 try:
#                     parsed_result = json.loads(result_text)
#                     return ActionResult(
#                         success=True,
#                         result=parsed_result,
#                         tool_name=tool_call.tool_name
#                     )
#                 except json.JSONDecodeError:
#                     # Plain text result
#                     return ActionResult(
#                         success=True,
#                         result=result_text,
#                         tool_name=tool_call.tool_name
#                     )
#             else:
#                 return ActionResult(
#                     success=False,
#                     result=None,
#                     error_message="No content in tool result",
#                     tool_name=tool_call.tool_name
#                 )
                
#         except Exception as e:
#             return ActionResult(
#                 success=False,
#                 result=None,
#                 error_message=str(e),
#                 tool_name=tool_call.tool_name
#             )
    
#     def format_result_for_decision(self, action_result: ActionResult) -> str:
#         """Format action result for passing back to decision layer"""
#         if action_result.success:
#             return f"Tool '{action_result.tool_name}' succeeded: {json.dumps(action_result.result, indent=2)}"
#         else:
#             return f"Tool '{action_result.tool_name}' failed: {action_result.error_message}"


"""
Action Layer + MCP Tool Definitions
-----------------------------------
Deterministic execution layer that triggers registered MCP tools
and returns structured ActionResult objects.
"""

from pydantic import BaseModel, Field
from typing import Any, Optional
from mcp import ClientSession
from mcp.server.fastmcp import FastMCP
from rich.console import Console
from rich.panel import Panel
import json
import re
import sys

# ----------------------------------------------------------------------------
# MCP Server Initialization
# ----------------------------------------------------------------------------

console = Console(stderr=True, force_terminal=False)
mcp = FastMCP("MathIntegrationAgent")


# ----------------------------------------------------------------------------
# ACTION RESULT MODEL
# ----------------------------------------------------------------------------

class ActionResult(BaseModel):
    """Result of action execution"""
    success: bool = Field(description="Whether action succeeded")
    result: Any = Field(description="Tool execution result")
    error_message: Optional[str] = None
    tool_name: str = Field(description="Name of tool executed")


# ----------------------------------------------------------------------------
# ACTION LAYER CLASS
# ----------------------------------------------------------------------------

class ActionLayer:
    """Action cognitive layer - executes MCP tools"""

    def __init__(self, mcp_session: ClientSession):
        self.session = mcp_session

    async def execute(self, tool_call) -> ActionResult:
        """
        Execute a tool call

        Args:
            tool_call: ToolCall decision from decision layer

        Returns:
            ActionResult with execution outcome
        """
        try:
            tool_result = await self.session.call_tool(
                tool_call.tool_name,
                arguments=tool_call.arguments
            )

            if tool_result.content:
                result_text = tool_result.content[0].text
                try:
                    parsed_result = json.loads(result_text)
                    return ActionResult(
                        success=True,
                        result=parsed_result,
                        tool_name=tool_call.tool_name
                    )
                except json.JSONDecodeError:
                    return ActionResult(
                        success=True,
                        result=result_text,
                        tool_name=tool_call.tool_name
                    )
            else:
                return ActionResult(
                    success=False,
                    result=None,
                    error_message="No content in tool result",
                    tool_name=tool_call.tool_name
                )

        except Exception as e:
            return ActionResult(
                success=False,
                result=None,
                error_message=str(e),
                tool_name=tool_call.tool_name
            )

    def format_result_for_decision(self, action_result: ActionResult) -> str:
        """Format action result for passing back to decision layer"""
        if action_result.success:
            return f"Tool '{action_result.tool_name}' succeeded: {json.dumps(action_result.result, indent=2)}"
        else:
            return f"Tool '{action_result.tool_name}' failed: {action_result.error_message}"


# ----------------------------------------------------------------------------
# REGISTERED MCP TOOLS
# ----------------------------------------------------------------------------

@mcp.tool()
def show_reasoning(steps: list) -> str:
    """Show step-by-step reasoning process"""
    console.print("[blue]FUNCTION CALL:[/blue] show_reasoning()")
    for i, step in enumerate(steps, 1):
        console.print(Panel(f"{step}", title=f"Step {i}", border_style="cyan"))
    return "Reasoning shown"


@mcp.tool()
def parse_polynomial(expression: str) -> str:
    """Parse a polynomial expression into structured terms"""
    console.print("[blue]FUNCTION CALL:[/blue] parse_polynomial()")
    console.print(f"[blue]Input:[/blue] {expression}")

    expr = expression.replace(" ", "").replace("dx", "").replace("∫", "")
    pattern = r'([+-]?)(\d+\.?\d*)(x?)(\^?)(\d*\.?\d*)'
    matches = re.findall(pattern, expr)

    terms = []
    for match in matches:
        sign, coeff, has_x, has_caret, power_str = match
        if not coeff:
            continue

        coeff = float(coeff)
        if sign == '-':
            coeff = -coeff

        if not has_x:
            power = 0.0
        elif has_caret and power_str:
            power = float(power_str)
        elif has_x:
            power = 1.0
        else:
            power = 0.0

        terms.append({"coeff": coeff, "power": power})

    result = json.dumps(terms)
    console.print(f"[green]Parsed:[/green] {result}")
    return result


@mcp.tool()
def integrate_term(coeff: float, power: float) -> str:
    """Apply power rule to integrate a single term"""
    console.print(f"[blue]FUNCTION CALL:[/blue] integrate_term({coeff}, {power})")

    if power == -1:
        result = {"status": "error", "message": "logarithmic_case"}
    else:
        new_power = power + 1
        new_coeff = coeff / new_power
        result = {"status": "success", "coeff": new_coeff, "power": new_power}

    result_str = json.dumps(result)
    console.print(f"[green]Result:[/green] {result_str}")
    return result_str


@mcp.tool()
def differentiate_term(coeff: float, power: float) -> str:
    """Apply power rule to differentiate a term"""
    console.print(f"[blue]FUNCTION CALL:[/blue] differentiate_term({coeff}, {power})")

    if power == 0:
        result = {"status": "zero", "coeff": 0.0, "power": 0.0}
    else:
        new_coeff = coeff * power
        new_power = power - 1
        result = {"status": "success", "coeff": new_coeff, "power": new_power}

    result_str = json.dumps(result)
    console.print(f"[green]Derivative:[/green] {result_str}")
    return result_str


@mcp.tool()
def format_polynomial_latex(terms: list) -> str:
    """Convert polynomial terms to LaTeX string"""
    console.print("[blue]FUNCTION CALL:[/blue] format_polynomial_latex()")
    from fractions import Fraction

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
    console.print(f"[green]LaTeX:[/green] {result}")
    return result


@mcp.tool()
def compare_polynomials(original_terms: list, verified_terms: list) -> str:
    """Compare two polynomial term lists for equality"""
    console.print("[blue]FUNCTION CALL:[/blue] compare_polynomials()")

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
        console.print("[green]✓ VERIFIED[/green]")
    else:
        discrepancies = []
        all_powers = set(orig_norm.keys()) | set(verif_norm.keys())
        for p in sorted(all_powers, reverse=True):
            orig_c = orig_norm.get(p, 0)
            verif_c = verif_norm.get(p, 0)
            if abs(orig_c - verif_c) > 1e-9:
                discrepancies.append({"power": p, "expected": orig_c, "got": verif_c})
        result = {"status": "fail", "message": "Verification failed", "discrepancies": discrepancies}
        console.print("[red]✗ FAILED[/red]")

    return json.dumps(result)


@mcp.tool()
def integrate_symbolic(expression: str, variable: str = "x") -> str:
    """Integrate any expression using SymPy"""
    console.print(f"[blue]FUNCTION CALL:[/blue] integrate_symbolic({expression}, {variable})")
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
        console.print(f"[green]Result:[/green] {result['latex']}")
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
def differentiate_symbolic(expression: str, variable: str = "x") -> str:
    """Differentiate expression using SymPy"""
    console.print(f"[blue]FUNCTION CALL:[/blue] differentiate_symbolic({expression}, {variable})")
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
        console.print(f"[green]Derivative:[/green] {result['latex']}")
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


@mcp.tool()
def verify_symbolic_integration(original: str, antiderivative: str, variable: str = "x") -> str:
    """Verify integration by differentiating"""
    console.print("[blue]FUNCTION CALL:[/blue] verify_symbolic_integration()")
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
        console.print("[green]✓ VERIFIED[/green]" if is_equal else "[red]✗ FAILED[/red]")
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ----------------------------------------------------------------------------
# ENTRY POINT
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "dev":
            mcp.run()
        else:
            mcp.run(transport="stdio")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
