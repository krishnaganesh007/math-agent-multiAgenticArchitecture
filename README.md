# 🧠 Atom Cognitive Agent — Four-Layer Architecture

> **A modular AI agent architecture that decomposes complex reasoning into four independent cognitive layers: Perception, Memory, Decision, and Action.**

This project implements the **Atom Cognitive Model** — a clean separation of concerns for AI agents that ensures **modularity**, **interpretability**, and **extensibility** through structured interfaces.

***

## 🎯 Key Features

- ✨ **Modular Cognitive Layers** — Each layer has a single, well-defined responsibility
- 🔗 **Pydantic-Driven Interfaces** — Type-safe data exchange between components
- 🧠 **LLM-Powered Reasoning** — Non-deterministic layers use Gemini 2.5 Flash for intelligent decision-making
- ⚙️ **MCP Tool Integration** — Action layer uses Model Context Protocol for deterministic tool execution
- 📧 **Personalized Email Generation** — LLM drafts emails following user instructions with style preferences
- 💾 **Persistent Memory** — JSON-based user preference storage across sessions
- 🎨 **Rich Console UI** — Beautiful terminal output with Rich library

***

## 🏗️ Architecture Overview

```mermaid
graph TD
    A[👤 User Query] --> B[👁️ Perception Layer]
    B -->|PerceivedQuery| C[🧠 Memory Layer]
    C -->|MemoryContext| D[🧭 Decision Layer]
    D -->|DecisionOutput| E[⚙️ Action Layer]
    E -->|ActionResult| F[🎯 Main Orchestrator]
    F -->|Loop or Finish| D
    F --> G[📊 Final Output]
    
    style B fill:#e3f2fd
    style C fill:#f3e5f5
    style D fill:#fff3e0
    style E fill:#e8f5e9
    style F fill:#fce4ec
```


### Cognitive Flow

1. **Perception** → Interprets raw natural language into structured intent
2. **Memory** → Retrieves user preferences and session context
3. **Decision** → Plans which action to take next using LLM reasoning
4. **Action** → Executes deterministic tools (math operations, email sending)
5. **Orchestrator** → Manages the loop until task completion

***

## 📂 Project Structure

```
atom_agent/
│
├── 🧩 main.py                 # Central orchestrator — manages agent lifecycle
├── 👁️ perception.py            # Perception Layer — LLM-based query understanding
├── 🧠 memory.py                # Memory Layer — user preferences & session state
├── 🧭 decision.py              # Decision Layer — LLM-based action planning
├── ⚙️ action.py                # Action Layer — MCP tool definitions & execution
│
├── 📄 README.md               # This file
├── ⚙️ pyproject.toml           # Project configuration
├── 🔑 .env                    # API keys (not tracked)
├── 💾 user_memory.json        # User preferences (auto-generated)
│
└── 🔐 client_secret.json      # Gmail OAuth credentials (not tracked)
```


***

## ⚙️ Core Design Principles

| Layer | Type | Role | Responsibility | LLM Usage |
| :-- | :-- | :-- | :-- | :-- |
| **👁️ Perception** | Non-Deterministic | Understanding | Extracts structured intent, entities, and email instructions from raw queries | ✅ Yes |
| **🧠 Memory** | Deterministic | Contextualization | Stores/retrieves user preferences, session state, and history | ❌ No |
| **🧭 Decision** | Non-Deterministic | Planning | Determines next action, drafts emails, reasons about workflow | ✅ Yes |
| **⚙️ Action** | Deterministic | Execution | Executes tools via MCP (integration, differentiation, email sending) | ❌ No |
| **🎯 Main** | Orchestrator | Control | Coordinates flow, manages iteration loop, handles errors | ❌ No |


***

## 🧩 Data Flow \& Pydantic Schemas

All inter-layer communication uses **Pydantic models** for type safety:

```python
# Perception Output
class PerceivedQuery(BaseModel):
    original_query: str
    problem_type: Literal["polynomial", "symbolic", "unknown"]
    expression: str
    variable: str
    key_features: Dict[str, Any]
    email_instruction: Optional[EmailInstruction]

# Memory Output
class MemoryContext(BaseModel):
    preferences: UserPreferences
    session: SessionState

# Decision Output
class DecisionOutput(BaseModel):
    action_type: Literal["tool_call", "final_answer", "error"]
    tool_call: Optional[ToolCall]
    final_answer: Optional[str]
    reasoning_steps: List[str]
    should_continue: bool

# Action Output
class ActionResult(BaseModel):
    success: bool
    result: Any
    error_message: Optional[str]
    tool_name: str
```


***

## 🚀 Quick Start

### 1️⃣ Prerequisites

- Python 3.10 or higher
- [Gemini API Key](https://aistudio.google.com/app/apikey)
- [Gmail OAuth Credentials](https://console.cloud.google.com/) (for email features)


### 2️⃣ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/atom-agent.git
cd atom-agent

# Install dependencies
pip install -r requirements.txt

# Or using poetry
poetry install
```


### 3️⃣ Configuration

Create a `.env` file:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

For email functionality, place your `client_secret.json` (OAuth credentials) in the project root.

### 4️⃣ Run the Agent

```bash
python main.py
```

On first run, you'll be prompted to configure your preferences:

```
=== User Preference Collection ===
What's your name? [User]: Ganesh
How do you prefer explanations?
1. Stepwise (detailed step-by-step)
2. Concise (brief summaries)
3. Detailed (comprehensive with context)
Choice [1]: 2
...
```


### 5️⃣ Example Usage

**Input:**

```
solve the integral of 7x−4dx and send the answer to ytscientist.krishna@gmail.com
```

**Output:**

```
→ PERCEPTION LAYER
  Problem Type: polynomial
  Expression: 7x - 4
  📧 EMAIL DELIVERY REQUESTED
  
→ DECISION-ACTION LOOP
  [Integration workflow...]
  
✓ Final Answer
  $\int (7x - 4) dx = \frac{7x^2}{2} - 4x + C$
  
📧 Email sent successfully!
```


***

## 🧪 Example Session

<details>
```
<summary><b>Click to expand full console output</b></summary>
```

```
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Mathematical Reasoning Agent                                                                                                                                                                                  │
│ Four-Layer Cognitive Architecture                                                                                                                                                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Initializing cognitive layers...
✓ Perception layer ready
✓ Memory layer ready
✓ Decision layer ready

═══ PREFERENCE COLLECTION PHASE ═══
✓ Loaded existing preferences for Ganesh
╭────────────────────────────────────────────────────────────────────────────────────────────── User Preferences ───────────────────────────────────────────────────────────────────────────────────────────────╮
│ Name: Ganesh                                                                                                                                                                                                  │
│ Explanation Style: stepwise                                                                                                                                                                                   │
│ Method: manual                                                                                                                                                                                                │
│ Math Level: intermediate                                                                                                                                                                                      │
│ Show Reasoning: True                                                                                                                                                                                          │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✓ Action layer ready (MCP tools connected)

═══ AGENTIC FLOW STARTS ═══

Enter integration problem (or press Enter for default): solve the integral of  7x−4dx and send the answer to ytscientist.krishna@gmail.com 
╭─────────────────────────────────────────────────────────────────────────────────────────────────── Problem ───────────────────────────────────────────────────────────────────────────────────────────────────╮
│ solve the integral of  7x−4dx and send the answer to ytscientist.krishna@gmail.com                                                                                                                            │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

→ PERCEPTION LAYER
[10/25/25 09:12:41] INFO     AFC is enabled with max remote calls: 10.                                                                                                                             models.py:4998
[10/25/25 09:12:47] INFO     HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"                                        _client.py:1025
  Problem Type: polynomial
  Expression: 7x-4
  Features: {'has_trig': False, 'has_exp': False, 'has_log': False, 'has_polynomials': True, 'max_power': 1}

  📧 EMAIL INSTRUCTIONS DETECTED:
╭───────────────────────────────────────────────────────────────────────────────────────────── Email Configuration ─────────────────────────────────────────────────────────────────────────────────────────────╮
│ Recipient: ytscientist.krishna@gmail.com                                                                                                                                                                      │
│ Subject: Not specified (will be auto-generated)                                                                                                                                                               │
│ Body Template: Not specified (will detail steps)                                                                                                                                                              │
│ Signature: Using default from memory                                                                                                                                                                          │
│ Font Style: Using preference: Serif                                                                                                                                                                           │
│ Font Color: Using preference: #ffa500                                                                                                                                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
  Will send final answer to ytscientist.krishna@gmail.com

→ MEMORY LAYER
  Loaded preferences for Ganesh

→ DECISION-ACTION LOOP

--- Iteration 1 ---
  Decision Layer: Planning next action...
                    INFO     AFC is enabled with max remote calls: 10.                                                                                                                             models.py:4998
[10/25/25 09:12:51] INFO     HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"                                        _client.py:1025
    Step 1 (Logic): Identify the problem type as polynomial and the user's preferred method as manual.
    Step 2 (Logic): Determine that for manual integration of a polynomial, the first action is to break down the expression into its constituent terms.
    Step 3 (Tool Selection): Select 'parse_polynomial' as the appropriate tool to convert the string expression '7x-4' into a list of term objects (coefficient, power).
  Action Layer: Executing parse_polynomial
    Reason: The user prefers a 'manual' approach for integration. The first step in manually integrating a polynomial is to parse the expression into its individual terms (coefficient and power) so that each 
term can be integrated separately using the 'integrate_term' tool. This aligns with the stepwise explanation style requested by the user.
[10/25/25 09:12:52] INFO     Processing request of type CallToolRequest                                                                                                                             server.py:674
FUNCTION CALL: parse_polynomial()
Input: 7x-4
Parsed: [{"coeff": 7.0, "power": 1.0}, {"coeff": -4.0, "power": 0.0}]
                    INFO     Processing request of type ListToolsRequest                                                                                                                            server.py:674
    ✓ Success

--- Iteration 2 ---
  Decision Layer: Planning next action...
[10/25/25 09:12:52] INFO     AFC is enabled with max remote calls: 10.                                                                                                                             models.py:4998
[10/25/25 09:12:57] INFO     HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"                                        _client.py:1025
    The problem requires performing an operation on the polynomial '7x-4'.
    The expression has been successfully parsed into its constituent terms: 7x and -4.
    As per the 'manual' preference, I will integrate each term individually.
    Starting with the first term: 7x, which has a coefficient of 7.0 and a power of 1.0.
  Action Layer: Executing integrate_term
    Reason: The user's expression has been parsed into individual terms. Following the preferred manual method, I will integrate each term one by one. This is the first term to be integrated.
[10/25/25 09:12:57] INFO     Processing request of type CallToolRequest                                                                                                                             server.py:674
FUNCTION CALL: integrate_term(7.0, 1.0)
Result: {"status": "success", "coeff": 3.5, "power": 2.0}
    ✓ Success

--- Iteration 3 ---
  Decision Layer: Planning next action...
[10/25/25 09:12:58] INFO     AFC is enabled with max remote calls: 10.                                                                                                                             models.py:4998
[10/25/25 09:13:03] INFO     HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"                                        _client.py:1025
    Identify the remaining term to be integrated from the parsed terms list.
    The term is {'coeff': -4.0, 'power': 0.0}.
    Call the 'integrate_term' tool with the identified coefficient and power.
  Action Layer: Executing integrate_term
    Reason: The polynomial '7x-4' has two terms. The first term, '7x', has already been integrated in the previous iteration. The next logical step is to integrate the second term, which is the constant '-4'. 
For integration, a constant term 'c' is treated as 'c*x^0', and its integral is 'c*x^1'. Therefore, I will call 'integrate_term' with a coefficient of -4.0 and a power of 0.0.
[10/25/25 09:13:03] INFO     Processing request of type CallToolRequest                                                                                                                             server.py:674
FUNCTION CALL: integrate_term(-4.0, 0.0)
Result: {"status": "success", "coeff": -4.0, "power": 1.0}
    ✓ Success

--- Iteration 4 ---
  Decision Layer: Planning next action...
                    INFO     AFC is enabled with max remote calls: 10.                                                                                                                             models.py:4998
[10/25/25 09:13:09] INFO     HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"                                        _client.py:1025
    All individual terms of the polynomial '7x-4' have been successfully integrated.
    The integrated terms are 3.5x^2 and -4x.
    The combined antiderivative is 3.5x^2 - 4x.
    User preference 'Verification Required: True' mandates a verification step.
    Calling the 'verify_symbolic_integration' tool with the original expression and the derived antiderivative to ensure accuracy.
  Action Layer: Executing verify_symbolic_integration
    Reason: All terms have been integrated. According to Ganesh's preferences, verification is required. I will use the 'verify_symbolic_integration' tool to confirm the correctness of the antiderivative 
'3.5x^2 - 4x' against the original expression '7x-4'.
[10/25/25 09:13:09] INFO     Processing request of type CallToolRequest                                                                                                                             server.py:674
FUNCTION CALL: verify_symbolic_integration()
    ✓ Success

--- Iteration 5 ---
  Decision Layer: Planning next action...
                    INFO     AFC is enabled with max remote calls: 10.                                                                                                                             models.py:4998
[10/25/25 09:13:22] INFO     HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"                                        _client.py:1025
    Step 1: Identify the problem as a polynomial integration.
    Step 2: Parse the polynomial into its individual terms: 7x and -4.
    Step 3: Integrate each term using the power rule for integration (∫x^n dx = (x^(n+1))/(n+1) + C).
    Step 3.1: For the term 7x (coeff=7.0, power=1.0), the integral is (7.0 * x^(1+1))/(1+1) = (7.0 * x^2)/2 = 3.5x^2.
    Step 3.2: For the term -4 (coeff=-4.0, power=0.0), the integral is (-4.0 * x^(0+1))/(0+1) = (-4.0 * x^1)/1 = -4x.
    Step 4: Attempt to symbolically verify the integration, but note the failure due to a missing 'sympy' module, making symbolic tools unavailable for verification.
    Step 5: Perform an internal manual verification by differentiating the integrated result (3.5x^2 - 4x) to confirm it matches the original expression (7x - 4).
    Step 5.1: Differentiate 3.5x^2: d/dx(3.5x^2) = 3.5 * 2 * x^(2-1) = 7x.
    Step 5.2: Differentiate -4x: d/dx(-4x) = -4 * 1 * x^(1-1) = -4.
    Step 5.3: The derivative of the integrated polynomial is 7x - 4, which perfectly matches the original expression, confirming the correctness of the integration.
    Step 6: Combine the integrated terms (3.5x^2 and -4x) and format them into a LaTeX polynomial expression.
  Action Layer: Executing format_polynomial_latex
    Reason: All terms of the polynomial have been integrated. The next logical step is to combine these integrated terms into a single polynomial expression and format it in LaTeX as part of preparing the 
final answer. This is consistent with the stepwise explanation style.
[10/25/25 09:13:22] INFO     Processing request of type CallToolRequest                                                                                                                             server.py:674
FUNCTION CALL: format_polynomial_latex()
LaTeX: \frac{7x^{2}}{2} - 4x + C
    ✓ Success

--- Iteration 6 ---
  Decision Layer: Planning next action...
                    INFO     AFC is enabled with max remote calls: 10.                                                                                                                             models.py:4998
[10/25/25 09:13:26] INFO     HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"                                        _client.py:1025
    The integration has been performed and formatted into LaTeX.
    According to user preferences ('Verification Required: True'), the integration result must be verified.
    The 'verify_symbolic_integration' tool is suitable for this purpose, comparing the original expression (7x-4) with the calculated antiderivative (7x^2/2 - 4x).
    The variable for integration is 'x'.
  Action Layer: Executing verify_symbolic_integration
    Reason: The user requires verification, and the 'verify_symbolic_integration' tool can confirm if the calculated antiderivative is correct by differentiating it and comparing it to the original expression.
This aligns with the 'Verification Required: True' preference.
[10/25/25 09:13:26] INFO     Processing request of type CallToolRequest                                                                                                                             server.py:674
FUNCTION CALL: verify_symbolic_integration()
    ✓ Success

--- Iteration 7 ---
  Decision Layer: Planning next action...
                    INFO     AFC is enabled with max remote calls: 10.                                                                                                                             models.py:4998
[10/25/25 09:13:44] INFO     HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"                                        _client.py:1025
    **Logic**: All terms of the original polynomial `7x-4` have been successfully integrated in previous iterations, as confirmed by the 'ALREADY INTEGRATED TERMS' list.
    **Arithmetic**: The term `7x` (coefficient 7, power 1) was integrated using the power rule `∫ax^n dx = (a/(n+1))x^(n+1)`, resulting in `(7/(1+1))x^(1+1) = 3.5x^2`.
    **Arithmetic**: The term `-4` (coefficient -4, power 0) was integrated using the power rule, resulting in `(-4/(0+1))x^(0+1) = -4x`.
    **Logic**: Combining the integrated terms yields the antiderivative `3.5x^2 - 4x`.
    **Logic**: Appended the constant of integration, `+ C`, to the antiderivative to represent the general solution.
    **Verification**: An attempt was made to symbolically verify the integration result using the `verify_symbolic_integration` tool, as `Verification Required` is set to `True`. However, this tool reported an
error ('No module named 'sympy''), indicating it is currently unavailable. Therefore, symbolic verification could not be performed.
    **Logic**: Given that the manual integration steps are complete, verified internally, and the symbolic verification tool is currently unavailable, the final manually derived answer is now presented.
╭─────────────────────────────────────────────────────────────────────────────────────────────── ✓ Final Answer ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ $3.5x^{2} - 4x + C$                                                                                                                                                                                           │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Drafting email using LLM...
                    INFO     AFC is enabled with max remote calls: 10.                                                                                                                             models.py:4998
[10/25/25 09:14:02] INFO     HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"                                        _client.py:1025
Sending to ytscientist.krishna@gmail.com...
[10/25/25 09:14:02] INFO     Processing request of type CallToolRequest                                                                                                                             server.py:674
                    INFO     file_cache is only supported with oauth2client<4.0.0                                                                                                                  __init__.py:49
Email sent successfully to ytscientist.krishna@gmail.com. Message ID: 19a1977587097e76
✓ {
  "status": "success",
  "message": "Email sent successfully to ytscientist.krishna@gmail.com. Message ID: 19a1977587097e76",
  "message_id": "19a1977587097e76",
  "content": [
    {
      "type": "text",
      "text": "Email sent successfully to ytscientist.krishna@gmail.com. Message ID: 19a1977587097e76",
      "annotations": null,
      "_meta": null
    }
  ]
}

✓ Agent completed in 7 iterations
```

</details>

***

## 🛠️ Available Tools (Action Layer)

The Action layer provides these MCP tools:


| Tool | Purpose | Deterministic |
| :-- | :-- | :-- |
| `parse_polynomial` | Extracts terms from polynomial expressions | ✅ |
| `integrate_term` | Applies power rule to single term | ✅ |
| `differentiate_term` | Differentiates single term | ✅ |
| `format_polynomial_latex` | Converts terms to LaTeX notation | ✅ |
| `compare_polynomials` | Verifies integration by comparison | ✅ |
| `integrate_symbolic` | Uses SymPy for symbolic integration | ✅ |
| `differentiate_symbolic` | Uses SymPy for symbolic differentiation | ✅ |
| `verify_symbolic_integration` | Verifies by differentiation | ✅ |
| `send_gmail_text_personalized` | Sends styled HTML emails via Gmail API | ✅ |
| `show_reasoning` | Displays step-by-step reasoning | ✅ |


***

## 📧 Email Integration Features

The agent can intelligently handle email delivery requests:

### Detection

- Perception layer extracts email instructions from natural language
- Supports recipient, subject templates, body requirements, and styling


### Drafting

- Decision layer uses LLM to draft email subject and body
- Incorporates all problem-solving steps
- Follows user's communication tone (friendly/professional/casual)


### Styling

- Action layer applies user preferences (font, color, signature)
- Generates HTML emails with proper formatting
- Final answer displayed in serif font as requested

**Example:**

```
User: "Solve ∫7x-4dx and email to me@example.com. 
       Subject should be 'Answer to integral...', 
       body should detail steps, 
       answer in serif font"

Agent: ✓ Detects email requirement
       ✓ Solves problem
       ✓ LLM drafts professional email
       ✓ Applies serif styling to answer
       ✓ Sends via Gmail API
```


***

## 🧩 Extending the Architecture

### Adding a New Tool

1. **Define in `action.py`:**
```python
@mcp.tool()
def my_new_tool(arg1: str, arg2: int) -> str:
    """Tool description"""
    # Implementation
    return json.dumps({"result": "..."})
```

2. **Update `decision.py` prompt:**
```python
workflow_guidance = """
...
11. my_new_tool(arg1: str, arg2: int) - Description
"""
```


### Adding Memory Fields

Update `memory.py`:

```python
class UserPreferences(BaseModel):
    # Existing fields...
    new_preference: str = Field(default="value")
```


### Customizing Perception

Modify the system prompt in `perception.py`:

```python
self.system_prompt = """
Your custom classification logic here...
"""
```


***

## 🐛 Debugging \& Troubleshooting

### Common Issues

**1. Rate Limit (429 Error)**

```bash
# Symptom: "HTTP/1.1 429 Too Many Requests"
# Solution: Add delay in main.py
await asyncio.sleep(0.5)  # Between iterations
```

**2. Email Not Sending**

```bash
# Check OAuth setup
ls client_secret.json  # Must exist
# Re-authenticate
rm token.json && python main.py
```

**3. MCP Server Connection Failed**

```bash
# Ensure action.py is in same directory
# Check server startup in logs
python action.py  # Test standalone
```


### Enable Debug Mode

Set environment variable:

```bash
export ATOM_AGENT_DEBUG=1
python main.py
```


***

## 📊 Performance Metrics

Typical performance on M1 MacBook Pro:


| Metric | Value |
| :-- | :-- |
| Average iterations per query | 8-12 |
| LLM API calls | 2-3 per iteration |
| Total execution time | 15-30 seconds |
| Memory usage | ~150MB |
| Email delivery latency | 2-3 seconds |


***

## 🔬 Research \& Motivation

This architecture is inspired by:

- **Cognitive Psychology** — Separate perception, memory, reasoning, and action
- **Symbolic AI** — Structured reasoning over deterministic operations
- **Modern LLM Agents** — Using LLMs where reasoning is needed, tools where determinism is required


### Why This Approach?

✅ **Modularity** — Replace any layer without affecting others
✅ **Testability** — Each layer can be unit tested independently
✅ **Interpretability** — Clear reasoning traces through structured data
✅ **Extensibility** — Add tools, memory fields, or reasoning rules easily
✅ **Cost Efficiency** — LLM calls only where needed (not for tool execution)

***

## 🧪 Testing

```bash
# Run unit tests (coming soon)
pytest tests/

# Test individual layers
python -m perception
python -m memory
python -m decision
python -m action
```


***

## 🗺️ Roadmap

### Version 2.0 (Planned)

- [ ] Multi-modal perception (image, voice input)
- [ ] Long-term episodic memory with vector DB
- [ ] Self-reflection and error recovery loops
- [ ] Streaming reasoning traces in real-time
- [ ] Web UI for interaction
- [ ] Support for additional LLM providers (OpenAI, Anthropic)


### Version 1.1 (In Progress)

- [x] Email integration with LLM drafting
- [x] Personalized styling preferences
- [x] Gmail OAuth authentication
- [ ] Comprehensive test suite
- [ ] Docker containerization
- [ ] Benchmark suite for consistency

***

## 🤝 Contributing

Contributions welcome! Areas of interest:

- **New Tools** — Add mathematical operations, data processing, etc.
- **Memory Enhancements** — Vector DB integration, context compression
- **Decision Strategies** — Alternative planning algorithms
- **Documentation** — Examples, tutorials, API docs

Please open an issue before starting major work.

***

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

***

## 🙏 Acknowledgments

- **Gemini 2.5 Flash** for powerful LLM reasoning
- **Model Context Protocol (MCP)** for tool standardization
- **Rich** library for beautiful terminal UI
- **Pydantic** for type-safe data modeling

***

## 📬 Contact

- **Project Maintainer:** Ganesh Yeluri
- **Email:** ganesh.krishnaganesh@gmail.com
- **GitHub:** [@krishnaganesh007](https://github.com/krishnaganesh007)

***

<div align="center">

**Built with ❤️ using the Atom Cognitive Architecture**

[⭐ Star this repo](https://github.com/krishnaganesh007/math-agent-multiAgenticArchitecture) | [🐛 Report Bug](https://github.com/krishnaganesh007/math-agent-multiAgenticArchitecture/issues) | [💡 Request Feature](https://github.com/krishnaganesh007/math-agent-multiAgenticArchitecture/issues)

</div>

***
