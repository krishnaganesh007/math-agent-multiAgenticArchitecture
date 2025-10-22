"""
Main Orchestrator: Integrates all four cognitive layers
Manages the agent loop and coordinates between layers
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.panel import Panel

from perception import PerceptionLayer, PerceivedQuery
from memory import MemoryLayer, MemoryContext
from decision import DecisionLayer, DecisionOutput
from action import ActionLayer, ActionResult


console = Console()


async def main():
    """Main orchestrator function"""
    
    console.print(Panel(
        "[bold cyan]Mathematical Reasoning Agent[/bold cyan]\n"
        "Four-Layer Cognitive Architecture",
        border_style="cyan"
    ))
    
    # Initialize all cognitive layers
    console.print("\n[yellow]Initializing cognitive layers...[/yellow]")
    
    perception = PerceptionLayer()
    memory = MemoryLayer(memory_file="user_memory.json")
    decision = DecisionLayer()
    
    console.print("✓ Perception layer ready")
    console.print("✓ Memory layer ready")
    console.print("✓ Decision layer ready")
    
    # STEP 1: Collect user preferences (BEFORE agentic flow)
    console.print("\n[bold yellow]═══ PREFERENCE COLLECTION PHASE ═══[/bold yellow]")
    
    # Check if preferences exist, otherwise collect them
    if not memory.memory_file.exists():
        memory.collect_preferences_interactive()
    else:
        console.print(f"[green]✓ Loaded existing preferences for {memory.preferences.name}[/green]")
    
    # Display loaded preferences
    prefs = memory.preferences
    console.print(Panel(
        f"Name: {prefs.name}\n"
        f"Explanation Style: {prefs.preferred_explanation_style}\n"
        f"Method: {prefs.preferred_method}\n"
        f"Math Level: {prefs.math_level}\n"
        f"Show Reasoning: {prefs.show_reasoning}",
        title="User Preferences",
        border_style="green"
    ))
    
    # STEP 2: Start MCP server for action layer
    server_params = StdioServerParameters(
        command="python",
        args=["tools.py"]  # Your tools file
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            console.print("✓ Action layer ready (MCP tools connected)\n")
            
            action = ActionLayer(mcp_session=session)
            
            # STEP 3: Get user problem
            console.print("[bold yellow]═══ AGENTIC FLOW STARTS ═══[/bold yellow]\n")
            
            # Example problems - you can make this interactive
            problem = input("Enter integration problem (or press Enter for default): ").strip()
            if not problem:
                problem = "∫4x^6 - 2x^3 + 7x - 4 dx"
            
            console.print(Panel(f"[bold]{problem}[/bold]", title="Problem", border_style="cyan"))
            
            # STEP 4: PERCEPTION (called once)
            console.print("\n[blue]→ PERCEPTION LAYER[/blue]")
            perceived: PerceivedQuery = await perception.perceive(problem)
            
            console.print(f"  Problem Type: {perceived.problem_type}")
            console.print(f"  Expression: {perceived.expression}")
            console.print(f"  Features: {perceived.key_features}")
            
            # STEP 5: MEMORY (called once to get context)
            console.print("\n[blue]→ MEMORY LAYER[/blue]")
            memory.update_session(
                current_problem=problem,
                iteration_count=0
            )
            memory_context: MemoryContext = memory.get_context()
            console.print(f"  Loaded preferences for {memory_context.preferences.name}")
            
            # STEP 6: DECISION-ACTION LOOP
            console.print("\n[blue]→ DECISION-ACTION LOOP[/blue]")
            
            max_iterations = 25
            iteration = 0
            tool_result_text = None
            
            while iteration < max_iterations:
                iteration += 1
                memory.update_session(iteration_count=iteration)
                
                console.print(f"\n[dim]--- Iteration {iteration} ---[/dim]")
                
                # DECISION
                console.print("[blue]  Decision Layer:[/blue] Planning next action...")
                decision_output: DecisionOutput = await decision.decide(
                    perceived=perceived,
                    memory=memory.get_context(),
                    tool_result=tool_result_text
                )
                
                # Display reasoning if user prefers
                if memory.preferences.show_reasoning and decision_output.reasoning_steps:
                    for step in decision_output.reasoning_steps:
                        console.print(f"    [dim]{step}[/dim]")
                
                # Handle decision
                if decision_output.action_type == "final_answer":
                    console.print(Panel(
                        f"[bold green]{decision_output.final_answer}[/bold green]",
                        title="✓ Final Answer",
                        border_style="green"
                    ))
                    break
                
                elif decision_output.action_type == "tool_call":
                    tool_call = decision_output.tool_call
                    console.print(f"[blue]  Action Layer:[/blue] Executing {tool_call.tool_name}")
                    console.print(f"    [dim]Reason: {tool_call.reasoning}[/dim]")
                    
                    # ACTION
                    action_result: ActionResult = await action.execute(tool_call)
                    
                    if action_result.success:
                        console.print(f"    [green]✓ Success[/green]")
                        
                        # Update memory with results
                        if tool_call.tool_name == "parse_polynomial":
                            memory.update_session(parsed_terms=action_result.result)
                        elif tool_call.tool_name == "integrate_term":
                            memory.session.integrated_terms.append(action_result.result)
                        elif tool_call.tool_name == "differentiate_term":
                            memory.session.differentiated_terms.append(action_result.result)
                        
                        # Add to history
                        memory.add_to_history({
                            "iteration": iteration,
                            "tool": tool_call.tool_name,
                            "result": action_result.result
                        })
                    else:
                        console.print(f"    [red]✗ Failed: {action_result.error_message}[/red]")
                    
                    # Format result for next decision
                    tool_result_text = action.format_result_for_decision(action_result)
                
                elif decision_output.action_type == "error":
                    console.print(f"[red]Error: {decision_output.error_message}[/red]")
                    break
                
                if not decision_output.should_continue:
                    break
            
            if iteration >= max_iterations:
                console.print("[red]Warning: Max iterations reached[/red]")
            
            console.print(f"\n[green]✓ Agent completed in {iteration} iterations[/green]")
            
            # Save session to memory
            memory.save_preferences()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Agent interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        import traceback
        traceback.print_exc()
