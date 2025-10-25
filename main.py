# """
# Main Orchestrator: Integrates all four cognitive layers
# Manages the agent loop and coordinates between layers
# """

# import asyncio
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# from rich.console import Console
# from rich.panel import Panel

# from perception import PerceptionLayer, PerceivedQuery
# from memory import MemoryLayer, MemoryContext
# from decision import DecisionLayer, DecisionOutput
# from action import ActionLayer, ActionResult


# console = Console()


# async def main():
#     """Main orchestrator function"""
    
#     console.print(Panel(
#         "[bold cyan]Mathematical Reasoning Agent[/bold cyan]\n"
#         "Four-Layer Cognitive Architecture",
#         border_style="cyan"
#     ))
    
#     # Initialize all cognitive layers
#     console.print("\n[yellow]Initializing cognitive layers...[/yellow]")
    
#     perception = PerceptionLayer()
#     memory = MemoryLayer(memory_file="user_memory.json")
#     decision = DecisionLayer()
    
#     console.print("✓ Perception layer ready")
#     console.print("✓ Memory layer ready")
#     console.print("✓ Decision layer ready")
    
#     # STEP 1: Collect user preferences (BEFORE agentic flow)
#     console.print("\n[bold yellow]═══ PREFERENCE COLLECTION PHASE ═══[/bold yellow]")
    
#     # Check if preferences exist, otherwise collect them
#     if not memory.memory_file.exists():
#         memory.collect_preferences_interactive()
#     else:
#         console.print(f"[green]✓ Loaded existing preferences for {memory.preferences.name}[/green]")
    
#     # Display loaded preferences
#     prefs = memory.preferences
#     console.print(Panel(
#         f"Name: {prefs.name}\n"
#         f"Explanation Style: {prefs.preferred_explanation_style}\n"
#         f"Method: {prefs.preferred_method}\n"
#         f"Math Level: {prefs.math_level}\n"
#         f"Show Reasoning: {prefs.show_reasoning}",
#         title="User Preferences",
#         border_style="green"
#     ))
    
#     # STEP 2: Start MCP server for action layer
#     server_params = StdioServerParameters(
#         command="python",
#         args=["tools.py"]  # Your tools file
#     )
    
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()
#             console.print("✓ Action layer ready (MCP tools connected)\n")
            
#             action = ActionLayer(mcp_session=session)
            
#             # STEP 3: Get user problem
#             console.print("[bold yellow]═══ AGENTIC FLOW STARTS ═══[/bold yellow]\n")
            
#             # Example problems - you can make this interactive
#             problem = input("Enter integration problem (or press Enter for default): ").strip()
#             if not problem:
#                 problem = "∫4x^6 - 2x^3 + 7x - 4 dx"
            
#             console.print(Panel(f"[bold]{problem}[/bold]", title="Problem", border_style="cyan"))
            
#             # STEP 4: PERCEPTION (called once)
#             console.print("\n[blue]→ PERCEPTION LAYER[/blue]")
#             perceived: PerceivedQuery = await perception.perceive(problem)
            
#             console.print(f"  Problem Type: {perceived.problem_type}")
#             console.print(f"  Expression: {perceived.expression}")
#             console.print(f"  Features: {perceived.key_features}")
            
#             # STEP 5: MEMORY (called once to get context)
#             console.print("\n[blue]→ MEMORY LAYER[/blue]")
#             memory.update_session(
#                 current_problem=problem,
#                 iteration_count=0
#             )
#             memory_context: MemoryContext = memory.get_context()
#             console.print(f"  Loaded preferences for {memory_context.preferences.name}")
            
#             # STEP 6: DECISION-ACTION LOOP
#             console.print("\n[blue]→ DECISION-ACTION LOOP[/blue]")
            
#             max_iterations = 25
#             iteration = 0
#             tool_result_text = None
            
#             while iteration < max_iterations:
#                 iteration += 1
#                 memory.update_session(iteration_count=iteration)
                
#                 console.print(f"\n[dim]--- Iteration {iteration} ---[/dim]")
                
#                 # DECISION
#                 console.print("[blue]  Decision Layer:[/blue] Planning next action...")
#                 decision_output: DecisionOutput = await decision.decide(
#                     perceived=perceived,
#                     memory=memory.get_context(),
#                     tool_result=tool_result_text
#                 )
                
#                 # Display reasoning if user prefers
#                 if memory.preferences.show_reasoning and decision_output.reasoning_steps:
#                     for step in decision_output.reasoning_steps:
#                         console.print(f"    [dim]{step}[/dim]")
                
#                 # Handle decision
#                 if decision_output.action_type == "final_answer":
#                     console.print(Panel(
#                         f"[bold green]{decision_output.final_answer}[/bold green]",
#                         title="✓ Final Answer",
#                         border_style="green"
#                     ))
#                     break
                
#                 elif decision_output.action_type == "tool_call":
#                     tool_call = decision_output.tool_call
#                     console.print(f"[blue]  Action Layer:[/blue] Executing {tool_call.tool_name}")
#                     console.print(f"    [dim]Reason: {tool_call.reasoning}[/dim]")
                    
#                     # ACTION
#                     action_result: ActionResult = await action.execute(tool_call)
                    
#                     if action_result.success:
#                         console.print(f"    [green]✓ Success[/green]")
                        
#                         # Update memory with results
#                         if tool_call.tool_name == "parse_polynomial":
#                             memory.update_session(parsed_terms=action_result.result)
#                         elif tool_call.tool_name == "integrate_term":
#                             memory.session.integrated_terms.append(action_result.result)
#                         elif tool_call.tool_name == "differentiate_term":
#                             memory.session.differentiated_terms.append(action_result.result)
                        
#                         # Add to history
#                         memory.add_to_history({
#                             "iteration": iteration,
#                             "tool": tool_call.tool_name,
#                             "result": action_result.result
#                         })
#                     else:
#                         console.print(f"    [red]✗ Failed: {action_result.error_message}[/red]")
                    
#                     # Format result for next decision
#                     tool_result_text = action.format_result_for_decision(action_result)
                
#                 elif decision_output.action_type == "error":
#                     console.print(f"[red]Error: {decision_output.error_message}[/red]")
#                     break
                
#                 if not decision_output.should_continue:
#                     break
            
#             if iteration >= max_iterations:
#                 console.print("[red]Warning: Max iterations reached[/red]")
            
#             console.print(f"\n[green]✓ Agent completed in {iteration} iterations[/green]")
            
#             # Save session to memory
#             memory.save_preferences()


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         console.print("\n[yellow]Agent interrupted by user[/yellow]")
#     except Exception as e:
#         console.print(f"[red]Fatal error: {e}[/red]")
#         import traceback
#         traceback.print_exc()


## NEW CODE

# -------------------------
#VERSION 2

# """
# Main Orchestrator: Integrates all four cognitive layers
# Manages the agent loop and coordinates between layers
# Supports sending final answers via Gmail if requested
# """

# import asyncio
# import re
# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# from rich.console import Console
# from rich.panel import Panel

# from perception import PerceptionLayer, PerceivedQuery
# from memory import MemoryLayer, MemoryContext
# from decision import DecisionLayer, DecisionOutput
# from action import ActionLayer, ActionResult

# console = Console()


# async def main():
#     """Main orchestrator function"""
    
#     console.print(Panel(
#         "[bold cyan]Mathematical Reasoning Agent[/bold cyan]\n"
#         "Four-Layer Cognitive Architecture",
#         border_style="cyan"
#     ))
    
#     # Initialize cognitive layers
#     console.print("\n[yellow]Initializing cognitive layers...[/yellow]")
    
#     perception = PerceptionLayer()
#     memory = MemoryLayer(memory_file="user_memory.json")
#     decision = DecisionLayer()
    
#     console.print("✓ Perception layer ready")
#     console.print("✓ Memory layer ready")
#     console.print("✓ Decision layer ready")
    
#     # STEP 1: Collect user preferences
#     console.print("\n[bold yellow]═══ PREFERENCE COLLECTION PHASE ═══[/bold yellow]")
    
#     if not memory.memory_file.exists():
#         memory.collect_preferences_interactive()
#     else:
#         console.print(f"[green]✓ Loaded existing preferences for {memory.preferences.name}[/green]")
    
#     prefs = memory.preferences
#     console.print(Panel(
#         f"Name: {prefs.name}\n"
#         f"Explanation Style: {prefs.preferred_explanation_style}\n"
#         f"Method: {prefs.preferred_method}\n"
#         f"Math Level: {prefs.math_level}\n"
#         f"Show Reasoning: {prefs.show_reasoning}",
#         title="User Preferences",
#         border_style="green"
#     ))
    
#     # STEP 2: Start MCP server for action layer
#     server_params = StdioServerParameters(command="python", args=["action.py"])
    
#     async with stdio_client(server_params) as (read, write):
#         async with ClientSession(read, write) as session:
#             await session.initialize()
#             console.print("✓ Action layer ready (MCP tools connected)\n")
            
#             action = ActionLayer(mcp_session=session)
            
#             # STEP 3: Get user problem
#             console.print("[bold yellow]═══ AGENTIC FLOW STARTS ═══[/bold yellow]\n")
            
#             problem = input("Enter integration problem (or press Enter for default): ").strip()
#             if not problem:
#                 problem = "∫4x^6 - 2x^3 + 7x - 4 dx"
            
#             console.print(Panel(f"[bold]{problem}[/bold]", title="Problem", border_style="cyan"))
            
#             # STEP 4: PERCEPTION
#             console.print("\n[blue]→ PERCEPTION LAYER[/blue]")
#             perceived: PerceivedQuery = await perception.perceive(problem)
            
#             console.print(f"  Problem Type: {perceived.problem_type}")
#             console.print(f"  Expression: {perceived.expression}")
#             console.print(f"  Features: {perceived.key_features}")
            
#             # Detect email instruction from query (fallback if perception fails)
#             send_email = False
#             recipient_email = None
#             if hasattr(perceived, "email_instruction") and perceived.email_instruction:
#                 send_email = True
#                 # recipient_email = perceived.email_instruction.get("recipient")
#                 recipient_email = perceived.email_instruction.recipient
#                 email_subject = perceived.email_instruction.subject

#             else:
#                 email_match = re.search(r'[\w\.-]+@[\w\.-]+', problem)
#                 if email_match:
#                     send_email = True
#                     recipient_email = email_match.group(0)

#             if send_email:
#                 console.print(f"  [magenta]Will send final answer to {recipient_email}[/magenta]")
            
#             # STEP 5: MEMORY
#             console.print("\n[blue]→ MEMORY LAYER[/blue]")
#             memory.update_session(current_problem=problem, iteration_count=0)
#             memory_context: MemoryContext = memory.get_context()
#             console.print(f"  Loaded preferences for {memory_context.preferences.name}")
            
#             # STEP 6: DECISION-ACTION LOOP
#             console.print("\n[blue]→ DECISION-ACTION LOOP[/blue]")
            
#             max_iterations = 25
#             iteration = 0
#             tool_result_text = None
            
#             while iteration < max_iterations:
#                 iteration += 1
#                 memory.update_session(iteration_count=iteration)
                
#                 console.print(f"\n[dim]--- Iteration {iteration} ---[/dim]")
                
#                 # DECISION
#                 console.print("[blue]  Decision Layer:[/blue] Planning next action...")
#                 decision_output: DecisionOutput = await decision.decide(
#                     perceived=perceived,
#                     memory=memory.get_context(),
#                     tool_result=tool_result_text
#                 )
                
#                 if memory.preferences.show_reasoning and decision_output.reasoning_steps:
#                     for step in decision_output.reasoning_steps:
#                         console.print(f"    [dim]{step}[/dim]")
                
#                 # Handle decision
#                 if decision_output.action_type == "final_answer":
#                     final_ans = decision_output.final_answer
#                     console.print(Panel(
#                         f"[bold green]{final_ans}[/bold green]",
#                         title="✓ Final Answer",
#                         border_style="green"
#                     ))

#                     # Send email if required
#                     if send_email and recipient_email:
#                         console.print(f"[magenta]Sending final answer to {recipient_email}...[/magenta]")
#                         email_result = await action.session.call_tool(
#                             "send_gmail_text_personalized",
#                             arguments={
#                                 "to": recipient_email,
#                                 "subject": "Integration Result",
#                                 "body": final_ans,
#                                 "font_style": memory_context.preferences.font_style,
#                                 "font_color": memory_context.preferences.font_color,
#                                 "signature": memory_context.preferences.signature,
#                                 "tone": memory_context.preferences.communication_tone
#                             }
#                         )
#                         if email_result.content and email_result.content[0].text:
#                             console.print(f"[magenta]{email_result.content[0].text}[/magenta]")

#                     break
                
#                 elif decision_output.action_type == "tool_call":
#                     tool_call = decision_output.tool_call
#                     console.print(f"[blue]  Action Layer:[/blue] Executing {tool_call.tool_name}")
#                     console.print(f"    [dim]Reason: {tool_call.reasoning}[/dim]")
                    
#                     action_result: ActionResult = await action.execute(tool_call)
                    
#                     if action_result.success:
#                         console.print(f"    [green]✓ Success[/green]")
                        
#                         # Update memory
#                         if tool_call.tool_name == "parse_polynomial":
#                             memory.update_session(parsed_terms=action_result.result)
#                         elif tool_call.tool_name == "integrate_term":
#                             memory.session.integrated_terms.append(action_result.result)
#                         elif tool_call.tool_name == "differentiate_term":
#                             memory.session.differentiated_terms.append(action_result.result)
                        
#                         # Add to history
#                         memory.add_to_history({
#                             "iteration": iteration,
#                             "tool": tool_call.tool_name,
#                             "result": action_result.result
#                         })
#                     else:
#                         console.print(f"    [red]✗ Failed: {action_result.error_message}[/red]")
                    
#                     tool_result_text = action.format_result_for_decision(action_result)
                
#                 elif decision_output.action_type == "error":
#                     console.print(f"[red]Error: {decision_output.error_message}[/red]")
#                     break
                
#                 if not decision_output.should_continue:
#                     break
            
#             if iteration >= max_iterations:
#                 console.print("[red]Warning: Max iterations reached[/red]")
            
#             console.print(f"\n[green]✓ Agent completed in {iteration} iterations[/green]")
            
#             # Save session to memory
#             memory.save_preferences()


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         console.print("\n[yellow]Agent interrupted by user[/yellow]")
#     except Exception as e:
#         console.print(f"[red]Fatal error: {e}[/red]")
#         import traceback
#         traceback.print_exc()



## NEW CODE - VERSION 3:

"""
Main Orchestrator: Integrates all four cognitive layers
Manages the agent loop and coordinates between layers
Supports sending final answers via Gmail with full prompt instructions
"""

import asyncio
import re
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

    # Initialize cognitive layers
    console.print("\n[yellow]Initializing cognitive layers...[/yellow]")

    perception = PerceptionLayer()
    memory = MemoryLayer(memory_file="user_memory.json")
    decision = DecisionLayer()

    console.print("✓ Perception layer ready")
    console.print("✓ Memory layer ready")
    console.print("✓ Decision layer ready")

    # STEP 1: Collect user preferences
    console.print("\n[bold yellow]═══ PREFERENCE COLLECTION PHASE ═══[/bold yellow]")

    if not memory.memory_file.exists():
        memory.collect_preferences_interactive()
    else:
        console.print(f"[green]✓ Loaded existing preferences for {memory.preferences.name}[/green]")

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
    server_params = StdioServerParameters(command="python", args=["action.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            console.print("✓ Action layer ready (MCP tools connected)\n")

            action = ActionLayer(mcp_session=session)

            # STEP 3: Get user problem
            console.print("[bold yellow]═══ AGENTIC FLOW STARTS ═══[/bold yellow]\n")

            problem = input("Enter integration problem (or press Enter for default): ").strip()
            if not problem:
                problem = "∫4x^6 - 2x^3 + 7x - 4 dx"

            console.print(Panel(f"[bold]{problem}[/bold]", title="Problem", border_style="cyan"))

            # STEP 4: PERCEPTION
            console.print("\n[blue]→ PERCEPTION LAYER[/blue]")
            perceived: PerceivedQuery = await perception.perceive(problem)

            console.print(f"  Problem Type: {perceived.problem_type}")
            console.print(f"  Expression: {perceived.expression}")
            console.print(f"  Features: {perceived.key_features}")

            # ✨ NEW: Display email instructions if detected
            if perceived.email_instruction:
                email_inst = perceived.email_instruction
                console.print("\n[magenta]  📧 EMAIL INSTRUCTIONS DETECTED:[/magenta]")
                console.print(Panel(
                    f"[bold]Recipient:[/bold] {email_inst.recipient}\n"
                    f"[bold]Subject:[/bold] {email_inst.subject or 'Not specified (will be auto-generated)'}\n"
                    f"[bold]Body Template:[/bold] {email_inst.body_template or 'Not specified (will detail steps)'}\n"
                    f"[bold]Signature:[/bold] {email_inst.signature or 'Using default from memory'}\n"
                    f"[bold]Font Style:[/bold] {email_inst.font_style or 'Using preference: ' + prefs.font_style}\n"
                    f"[bold]Font Color:[/bold] {email_inst.font_color or 'Using preference: ' + prefs.font_color}",
                    title="Email Configuration",
                    border_style="magenta"
                ))
            else:
                console.print("  [dim]No email instructions detected[/dim]")

            # Detect email instructions
            send_email = False
            recipient_email = None
            email_subject = None
            email_font_style = None
            email_font_color = None
            email_signature = None
            email_tone = None

            if hasattr(perceived, "email_instruction") and perceived.email_instruction:
                send_email = True
                instr = perceived.email_instruction
                recipient_email = getattr(instr, "recipient", None)
                email_subject = getattr(instr, "subject", "Integration Result")
                email_font_style = getattr(instr, "font_style", prefs.font_style)
                email_font_color = getattr(instr, "font_color", prefs.font_color)
                email_signature = getattr(instr, "signature", prefs.signature)
                email_tone = getattr(instr, "tone", prefs.communication_tone)
            else:
                email_match = re.search(r'[\w\.-]+@[\w\.-]+', problem)
                if email_match:
                    send_email = True
                    recipient_email = email_match.group(0)
                    email_subject = "Integration Result"
                    email_font_style = prefs.font_style
                    email_font_color = prefs.font_color
                    email_signature = prefs.signature
                    email_tone = prefs.communication_tone

            if send_email:
                console.print(f"  [magenta]Will send final answer to {recipient_email}[/magenta]")

            # STEP 5: MEMORY
            console.print("\n[blue]→ MEMORY LAYER[/blue]")
            memory.update_session(current_problem=problem, iteration_count=0)
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

                if memory.preferences.show_reasoning and decision_output.reasoning_steps:
                    for step in decision_output.reasoning_steps:
                        console.print(f"    [dim]{step}[/dim]")

                # Handle decision
                # if decision_output.action_type == "final_answer":
                #     final_ans = decision_output.final_answer
                #     console.print(Panel(
                #         f"[bold green]{final_ans}[/bold green]",
                #         title="✓ Final Answer",
                #         border_style="green"
                #     ))

                #     # Send email if required
                #     if send_email and recipient_email:
                #         console.print(f"[magenta]Sending final answer to {recipient_email}...[/magenta]")

                #         # Safely get preferences from memory
                #         email_subject = getattr(memory_context.preferences, "email_subject", "Integration Result")
                #         email_font_style = getattr(memory_context.preferences, "font_style", "serif")
                #         email_font_color = getattr(memory_context.preferences, "font_color", "black")
                #         email_signature = getattr(memory_context.preferences, "signature", "Yours smartly,\nMath Agent")
                #         email_tone = getattr(memory_context.preferences, "communication_tone", "neutral")

                #         # Ensure all are strings
                #         email_subject = str(email_subject)
                #         email_font_style = str(email_font_style)
                #         email_font_color = str(email_font_color)
                #         email_signature = str(email_signature)
                #         email_tone = str(email_tone)

                #         # Call Gmail tool
                #         email_result = await action.session.call_tool(
                #             "send_gmail_text_personalized",
                #             arguments={
                #                 "to": recipient_email,
                #                 "subject": email_subject,
                #                 "body": final_ans,
                #                 "font_style": email_font_style,
                #                 "font_color": email_font_color,
                #                 "signature": email_signature,
                #                 "tone": email_tone
                #             }
                #         )

                #         if email_result.content and email_result.content[0].text:
                #             console.print(f"[magenta]{email_result.content[0].text}[/magenta]")
                # In main.py, replace the email sending section:

                if decision_output.action_type == "final_answer":
                    final_ans = decision_output.final_answer
                    console.print(Panel(
                        f"[bold green]{final_ans}[/bold green]",
                        title="✓ Final Answer",
                        border_style="green"
                    ))

                    # Send email if required
                    if send_email and recipient_email:
                        console.print(f"[magenta]Drafting email using LLM...[/magenta]")
                        
                        # Use Decision Layer to draft email content
                        email_draft = await decision.draft_email_content(
                            perceived=perceived,
                            memory=memory.get_context(),
                            final_answer=final_ans
                        )
                        
                        console.print(f"[magenta]Sending to {recipient_email}...[/magenta]")
                        
                        # Get styling preferences
                        font_style = memory.preferences.font_style
                        font_color = memory.preferences.font_color
                        signature = memory.preferences.signature
                        tone = memory.preferences.communication_tone
                        
                        # Send email with drafted content + styling
                        email_result = await action.session.call_tool(
                            "send_gmail_text_personalized",
                            arguments={
                                "to": recipient_email,
                                "subject": email_draft["subject"],
                                "body": email_draft["body"],
                                "font_style": font_style,
                                "font_color": font_color,
                                "signature": signature,
                                "tone": tone
                            }
                        )
                        
                        # ✅ CORRECT
                        if email_result.content and email_result.content[0].text:
                            console.print(f"[green]✓ {email_result.content[0].text}[/green]")

                    
                    break


                elif decision_output.action_type == "tool_call":
                    tool_call = decision_output.tool_call
                    console.print(f"[blue]  Action Layer:[/blue] Executing {tool_call.tool_name}")
                    console.print(f"    [dim]Reason: {tool_call.reasoning}[/dim]")

                    action_result: ActionResult = await action.execute(tool_call)

                    if action_result.success:
                        console.print(f"    [green]✓ Success[/green]")

                        # Update memory
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
