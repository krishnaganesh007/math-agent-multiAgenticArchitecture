"""
Action Layer: Executes tools based on decisions
Deterministic: Direct tool execution without LLM involvement
"""

from pydantic import BaseModel, Field
from typing import Any, Optional
from mcp import ClientSession
from decision import ToolCall
import json


# Pydantic Models
class ActionResult(BaseModel):
    """Result of action execution"""
    success: bool = Field(description="Whether action succeeded")
    result: Any = Field(description="Tool execution result")
    error_message: Optional[str] = None
    tool_name: str = Field(description="Name of tool executed")


class ActionLayer:
    """Action cognitive layer - executes tools"""
    
    def __init__(self, mcp_session: ClientSession):
        self.session = mcp_session
    
    async def execute(self, tool_call: ToolCall) -> ActionResult:
        """
        Execute a tool call
        
        Args:
            tool_call: ToolCall decision from decision layer
            
        Returns:
            ActionResult with execution outcome
        """
        try:
            # Call MCP tool
            tool_result = await self.session.call_tool(
                tool_call.tool_name,
                arguments=tool_call.arguments
            )
            
            # Extract result
            if tool_result.content:
                result_text = tool_result.content[0].text
                
                # Try to parse as JSON if possible
                try:
                    parsed_result = json.loads(result_text)
                    return ActionResult(
                        success=True,
                        result=parsed_result,
                        tool_name=tool_call.tool_name
                    )
                except json.JSONDecodeError:
                    # Plain text result
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
