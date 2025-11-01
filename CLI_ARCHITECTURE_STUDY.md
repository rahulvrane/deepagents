# DeepAgents CLI - Comprehensive Architecture Study

## Executive Summary

The DeepAgents CLI is a sophisticated, production-ready AI coding assistant built on LangGraph and LangChain. It provides an interactive REPL (Read-Eval-Print Loop) where users can chat with an AI agent that has access to file operations, shell commands, web search, and can spawn subagents for complex tasks.

**Key Innovation**: The CLI implements a complete agent-based development environment with persistent memory, human-in-the-loop (HITL) approval, streaming execution, and rich terminal UI.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Input Layer                         │
│  • Prompt Toolkit (multi-line, autocomplete, key bindings)  │
│  • File mentions (@file.py), slash commands (/clear)         │
│  • Bash commands (!ls), regular prompts                      │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                    Main CLI Loop (main.py)                   │
│  • Command routing (slash, bash, or agent)                   │
│  • Token tracking and session management                     │
│  • Auto-approve mode toggle                                  │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                 Agent Creation (agent.py)                    │
│  • Model selection (OpenAI/Anthropic)                        │
│  • Backend configuration (CompositeBackend)                  │
│  • Middleware stack assembly                                 │
│  • HITL configuration for sensitive tools                    │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│              Task Execution (execution.py)                   │
│  • Streaming agent output (dual-mode: messages + updates)    │
│  • File operation tracking and diffing                       │
│  • Todo list rendering                                       │
│  • HITL approval prompts with arrow key navigation          │
│  • Summary message detection and formatting                  │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│           Agent Runtime (DeepAgents Core)                    │
│  • create_deep_agent() with middleware                       │
│  • FilesystemMiddleware, SubAgentMiddleware, TodoMiddleware│
│  • AgentMemoryMiddleware (long-term memory)                 │
│  • ResumableShellToolMiddleware                             │
│  • InMemorySaver checkpointer                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Entry Points and Flow

### 1. Entry Point Chain

```python
# 1. Package entry (__main__.py)
python -m deepagents_cli

# 2. Console script entry (pyproject.toml)
deepagents

# Both call → cli_main() in main.py
```

### 2. Startup Sequence

```python
cli_main()
├── check_cli_dependencies()     # Verify rich, tavily, etc.
├── parse_args()                  # Handle commands (list, help, reset)
│   ├── list → list_agents()
│   ├── help → show_help()
│   ├── reset → reset_agent()
│   └── default → interactive mode
└── asyncio.run(main(agent_id, session_state))
    ├── create_model()            # OpenAI or Anthropic based on env
    ├── create_agent_with_config() # Build agent with middleware
    └── simple_cli()              # Enter main REPL loop
```

### 3. Main REPL Loop (simple_cli)

```python
async def simple_cli(agent, assistant_id, session_state, baseline_tokens):
    console.clear()
    console.print(DEEP_AGENTS_ASCII)  # Show banner
    console.print(tips and warnings)

    session = create_prompt_session()  # Prompt toolkit setup
    token_tracker = TokenTracker()

    while True:
        user_input = await session.prompt_async()

        if user_input.startswith("/"):
            handle_command()  # /clear, /help, /tokens, /quit
        elif user_input.startswith("!"):
            execute_bash_command()  # !ls, !git status
        elif user_input in ["quit", "exit", "q"]:
            break
        else:
            execute_task()  # Send to agent
```

---

## Core Components Deep Dive

### 1. Agent Creation (`agent.py`)

#### Model Selection

```python
def create_model():
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if openai_key:
        return ChatOpenAI(
            model=os.environ.get("OPENAI_MODEL", "gpt-5-mini"),
            temperature=0.7,
        )
    elif anthropic_key:
        return ChatAnthropic(
            model_name=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
            max_tokens=20000,
        )
    else:
        sys.exit(1)  # No API key configured
```

#### Backend Configuration

The CLI uses a **CompositeBackend** that routes file operations to different backends:

```python
# Long-term memory backend (agent-specific directory)
long_term_backend = FilesystemBackend(
    root_dir=~/.deepagents/{agent_id}/,
    virtual_mode=True
)

# Composite routing
backend = CompositeBackend(
    default=FilesystemBackend(),  # Current working directory
    routes={
        "/memories/": long_term_backend  # Persistent agent memory
    }
)
```

**How it works:**
- `/path/to/file` → routes to default backend (real filesystem, cwd)
- `/memories/notes.md` → routes to `~/.deepagents/{agent_id}/notes.md`
- This enables **persistent agent memory** across sessions

#### Middleware Stack

```python
agent_middleware = [
    AgentMemoryMiddleware(backend=long_term_backend, memory_path="/memories/"),
    ResumableShellToolMiddleware(workspace_root=os.getcwd()),
]
```

**AgentMemoryMiddleware:**
- Loads `/memories/agent.md` at startup
- Injects content into system prompt with `<agent_memory>` tags
- Allows agent to self-modify its instructions

**ResumableShellToolMiddleware:**
- Provides `shell` tool for bash execution
- Supports HITL approval before execution

#### Human-in-the-Loop Configuration

```python
interrupt_on = {
    "shell": {
        "allowed_decisions": ["approve", "reject"],
        "description": lambda tool_call, state, runtime: (
            f"Shell Command: {tool_call['args'].get('command')}\n"
            f"Working Directory: {os.getcwd()}"
        ),
    },
    "write_file": write_file_interrupt_config,
    "edit_file": edit_file_interrupt_config,
    "web_search": web_search_interrupt_config,
    "task": task_interrupt_config,  # Subagent spawning
}
```

**Sensitive tools require approval before execution** unless `--auto-approve` is set.

#### System Prompt Structure

```python
system_prompt = f"""
### Current Working Directory
The filesystem backend is currently operating in: `{Path.cwd()}`

### Memory System Reminder
Your long-term memory is stored in /memories/ and persists across sessions.

**IMPORTANT - Check memories before answering:**
- When asked "what do you know about X?" → Run `ls /memories/` FIRST
- When starting a task → Check if you have guides in /memories/
- Base answers on saved knowledge from /memories/ when available

### Human-in-the-Loop Tool Approval
Some tools require user approval. When rejected:
1. Accept the decision - do NOT retry
2. Suggest alternative approach
3. Never attempt the same rejected command again

### Web Search Tool Usage
... synthesize results, cite sources, never show raw JSON ...

### Todo List Management
Keep todos MINIMAL (3-6 items max), ask for approval before starting.
"""
```

Then **AgentMemoryMiddleware** injects:
```python
<agent_memory>
{contents of ~/.deepagents/{agent_id}/agent.md}
</agent_memory>

## Long-term Memory
You can update your own instructions by editing /memories/agent.md
...
```

---

### 2. Task Execution (`execution.py`)

This is the **heart of the CLI** - handles streaming, HITL, and rendering.

#### Execution Flow

```python
def execute_task(user_input, agent, assistant_id, session_state, token_tracker):
    # 1. Parse file mentions (@file.py → inject content)
    prompt_text, mentioned_files = parse_file_mentions(user_input)
    if mentioned_files:
        # Inject file contents into prompt
        for file_path in mentioned_files:
            content = file_path.read_text()
            final_input += f"\n### {file_path.name}\n```\n{content}\n```"

    # 2. Setup streaming
    config = {"configurable": {"thread_id": "main"}}
    file_op_tracker = FileOpTracker()
    status = console.status("Agent is thinking...")

    # 3. Stream agent responses (dual-mode!)
    for chunk in agent.stream(
        stream_input,
        stream_mode=["messages", "updates"],  # Key innovation!
        subgraphs=True,
        config=config,
    ):
        namespace, stream_mode, data = chunk

        if stream_mode == "updates":
            # Handle interrupts and todo updates
            if "__interrupt__" in data:
                # HITL approval required
                if session_state.auto_approve:
                    decisions = auto_approve_all()
                else:
                    decisions = prompt_for_tool_approval()

                # Resume agent with decision
                stream_input = Command(resume={"decisions": decisions})
                continue  # Restart streaming

            if "todos" in data:
                render_todo_list(data["todos"])

        elif stream_mode == "messages":
            message, metadata = data

            if isinstance(message, ToolMessage):
                # Tool results - only show errors
                if tool_name == "shell" and status != "success":
                    console.print(error_message)

                # Track file operations for diff display
                record = file_op_tracker.complete_with_message(message)
                if record:
                    render_file_operation(record)

            # Parse content blocks (Anthropic format)
            for block in message.content_blocks:
                if block["type"] == "text":
                    pending_text += block["text"]

                elif block["type"] == "reasoning":
                    # Extended thinking blocks (optional display)
                    pass

                elif block["type"] == "tool_call_chunk":
                    # Buffer and parse tool calls
                    buffer_tool_call(block)
                    if complete:
                        display_tool_call()
```

#### Dual-Mode Streaming

**Key Innovation**: The CLI uses `stream_mode=["messages", "updates"]` to get:
1. **Messages stream**: AI responses, tool calls, tool results
2. **Updates stream**: State changes, interrupts (HITL), todos

This allows **real-time HITL** without blocking the stream!

#### HITL Approval Flow

```python
def prompt_for_tool_approval(action_request, assistant_id):
    """Interactive approval with arrow key navigation."""

    # 1. Build preview (shows what the tool will do)
    preview = build_approval_preview(tool_name, tool_args, assistant_id)

    # 2. Display panel with description
    console.print(Panel("⚠️ Tool Action Requires Approval\n" + preview.details))

    # 3. Show diff for file operations
    if preview.diff:
        render_diff_block(preview.diff)

    # 4. Arrow key navigation (up/down to select, enter to confirm)
    options = ["approve", "reject"]
    selected = 0  # Start with approve

    # Terminal raw mode for arrow key detection
    while True:
        display_options_with_checkboxes()

        char = sys.stdin.read(1)
        if char == "\x1b":  # ESC (arrow keys)
            if next2 == "B":  # Down
                selected = (selected + 1) % 2
            elif next2 == "A":  # Up
                selected = (selected - 1) % 2
        elif char == "\r":  # Enter
            break

    # 5. Return decision
    return {"type": "approve"} if selected == 0 else {"type": "reject"}
```

**If rejected:**
```python
if suppress_resumed_output:
    console.print("Command rejected. Returning to prompt.")

    # Resume agent in background to update state properly
    def resume_after_rejection():
        agent.invoke(Command(resume=hitl_response), config=config)

    threading.Thread(target=resume_after_rejection, daemon=True).start()
    return
```

#### File Operation Tracking

```python
class FileOpTracker:
    """Tracks file operations to show diffs."""

    def start_operation(self, tool_name, args, tool_call_id):
        """Called when tool call starts."""
        if tool_name == "edit_file":
            # Save original content for diffing
            old_content = read_file(args["file_path"])
            self.pending[tool_call_id] = {
                "tool": tool_name,
                "args": args,
                "old_content": old_content,
            }

    def complete_with_message(self, message: ToolMessage):
        """Called when tool completes."""
        if tool_call_id in self.pending:
            operation = self.pending.pop(tool_call_id)

            if operation["tool"] == "edit_file":
                new_content = read_file(operation["args"]["file_path"])
                diff = generate_diff(old_content, new_content)

                return FileOpRecord(
                    tool="edit_file",
                    file_path=operation["args"]["file_path"],
                    diff=diff,
                )
```

**Renders:**
```
┌─ File Edit ─────────────────────────────────────┐
│ src/example.py                                  │
├─────────────────────────────────────────────────┤
│ - old line                                      │
│ + new line                                      │
└─────────────────────────────────────────────────┘
```

---

### 3. User Input Handling (`input.py`)

#### Prompt Session Configuration

```python
def create_prompt_session(assistant_id, session_state):
    # Key bindings
    kb = KeyBindings()

    @kb.add("c-t")  # Ctrl+T
    def _(event):
        """Toggle auto-approve mode."""
        session_state.toggle_auto_approve()
        event.app.invalidate()  # Refresh UI

    @kb.add("enter")  # Enter submits
    def _(event):
        buffer = event.current_buffer
        if buffer.complete_state:  # Completion menu active
            buffer.apply_completion(current_completion)
        elif buffer.text.strip():
            buffer.validate_and_handle()  # Submit

    @kb.add("escape", "enter")  # Alt+Enter
    def _(event):
        event.current_buffer.insert_text("\n")  # Newline

    @kb.add("c-e")  # Ctrl+E
    def _(event):
        event.current_buffer.open_in_editor()  # Open nano/vim

    session = PromptSession(
        message=HTML('<style fg="#ffffff">></style> '),
        multiline=True,
        key_bindings=kb,
        completer=merge_completers([
            CommandCompleter(),  # /clear, /help
            BashCompleter(),     # !ls, !git
            FilePathCompleter(), # @file.py
        ]),
        bottom_toolbar=get_bottom_toolbar(session_state),  # Show auto-approve status
    )

    return session
```

#### File Mentions Feature

```python
def parse_file_mentions(text: str) -> tuple[str, list[Path]]:
    """Extract @file mentions and return file paths."""
    pattern = r"@((?:[^\s@]|(?<=\\)\s)+)"
    matches = re.findall(pattern, text)

    files = []
    for match in matches:
        path = Path(match).expanduser().resolve()
        if path.exists() and path.is_file():
            files.append(path)

    return text, files
```

**Usage:**
```
User: "Refactor @src/main.py to use async"
  ↓
Prompt becomes:
"Refactor to use async

## Referenced Files

### main.py
Path: `/path/to/src/main.py`
```python
# ... full file content ...
```
```

#### Autocomplete System

**Three completers merged:**

1. **CommandCompleter**: `/clear`, `/help`, `/tokens`, `/quit`
2. **BashCompleter**: `!ls`, `!git status`, `!pytest`
3. **FilePathCompleter**: `@src/`, `@config/app.yaml` (case-insensitive!)

**Example:**
```
> @src/c<TAB>
  Completes to: @src/config.py
            or: @src/commands.py
```

---

### 4. Tools (`tools.py`)

#### Web Search Tool

```python
def web_search(query, max_results=5, topic="general", include_raw_content=False):
    """Search web using Tavily API."""
    search_docs = tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    return search_docs  # {results: [{title, url, content, score}], query}
```

**Important**: Tool docstring instructs agent to:
1. Read the 'content' field of results
2. Synthesize information
3. Cite sources
4. **NEVER show raw JSON to user**

#### HTTP Request Tool

```python
def http_request(url, method="GET", headers=None, data=None, params=None, timeout=30):
    """Make HTTP requests to APIs."""
    response = requests.request(method, url, ...)

    return {
        "success": response.status_code < 400,
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "content": response.json() or response.text,
        "url": response.url,
    }
```

---

### 5. Commands (`commands.py`)

#### Slash Commands

```python
def handle_command(command, agent, token_tracker):
    cmd = command.lower().strip().lstrip("/")

    if cmd in ["quit", "exit", "q"]:
        return "exit"

    if cmd == "clear":
        agent.checkpointer = InMemorySaver()  # Reset conversation
        token_tracker.reset()
        console.clear()
        return True

    if cmd == "help":
        show_interactive_help()
        return True

    if cmd == "tokens":
        token_tracker.display_session()  # Show input/output token counts
        return True

    return False  # Unknown command
```

#### Bash Commands

```python
def execute_bash_command(command):
    """Execute bash command (! prefix)."""
    cmd = command.strip().lstrip("!")

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=Path.cwd()
    )

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr, style="red")
```

---

### 6. Memory System (`agent_memory.py`)

#### AgentMemoryMiddleware

```python
class AgentMemoryMiddleware(AgentMiddleware):
    def __init__(self, backend, memory_path="/memories/"):
        self.backend = backend
        self.memory_path = memory_path

    def before_agent(self, state, runtime):
        """Load agent.md before first run."""
        if "agent_memory" not in state:
            file_data = self.backend.read("/agent.md")
            return {"agent_memory": file_data}

    def wrap_model_call(self, request, handler):
        """Inject agent memory into system prompt."""
        agent_memory = request.state.get("agent_memory", "")

        # Add to start of system prompt
        memory_section = f"<agent_memory>\n{agent_memory}\n</agent_memory>"
        request.system_prompt = memory_section + "\n\n" + request.system_prompt

        # Add memory documentation
        request.system_prompt += LONGTERM_MEMORY_SYSTEM_PROMPT.format(
            memory_path=self.memory_path
        )

        return handler(request)
```

#### Memory Files

**`~/.deepagents/{agent_id}/agent.md`:**
- Contains agent's self-defined instructions
- Loaded at startup via AgentMemoryMiddleware
- Agent can self-modify by editing this file
- Injected into system prompt with `<agent_memory>` tags

**Default content** (from `default_agent_prompt.md`):
```markdown
You are an AI assistant that helps with coding, research, and analysis.

# Core Role
Your role may be updated based on user feedback. Update this file to reflect guidance.

## Memory-First Protocol
**Before answering questions:**
- Check `ls /memories/` FIRST
- Read relevant memory files
- Base answers on saved knowledge

**When learning:**
- Save to `/memories/[topic].md`
- Verify by reading back

# Tone and Style
Be concise. Answer in <4 lines unless asked for detail.
Don't explain what you did unless asked.

## Tools
- execute_bash: Shell commands
- read_file, write_file, edit_file: File ops
- web_search: Documentation lookup
- http_request: API calls
```

---

## Data Flow Example

### User Request: "Add a feature to @src/main.py"

```
1. USER INPUT
   ┌─────────────────────────────────────────────┐
   │ User: "Add logging to @src/main.py"         │
   └────────────────┬────────────────────────────┘
                    │
2. INPUT PARSING (input.py:parse_file_mentions)
   ┌────────────────▼────────────────────────────┐
   │ • Extract "@src/main.py"                    │
   │ • Read file content                         │
   │ • Inject into prompt with markdown fence    │
   └────────────────┬────────────────────────────┘
                    │
3. AGENT CREATION (agent.py:create_agent_with_config)
   ┌────────────────▼────────────────────────────┐
   │ • Load ~/.deepagents/agent/agent.md         │
   │ • Inject into system prompt                 │
   │ • Setup HITL for write_file/edit_file       │
   │ • CompositeBackend: cwd + /memories/        │
   └────────────────┬────────────────────────────┘
                    │
4. AGENT EXECUTION (execution.py:execute_task)
   ┌────────────────▼────────────────────────────┐
   │ Stream: ["messages", "updates"]             │
   │ ┌──────────────────────────────────────┐   │
   │ │ AI: I'll add logging. First read...  │   │
   │ └──────────────────────────────────────┘   │
   │ ┌──────────────────────────────────────┐   │
   │ │ 📖 read_file(/src/main.py)           │   │
   │ └──────────────────────────────────────┘   │
   │ ┌──────────────────────────────────────┐   │
   │ │ AI: Now I'll add logging imports...  │   │
   │ └──────────────────────────────────────┘   │
   │ ┌──────────────────────────────────────┐   │
   │ │ ✂️ edit_file(/src/main.py, ...)      │   │
   │ │ [INTERRUPT - HITL approval needed]   │   │
   │ └──────────────────────────────────────┘   │
   └────────────────┬────────────────────────────┘
                    │
5. HITL APPROVAL (execution.py:prompt_for_tool_approval)
   ┌────────────────▼────────────────────────────┐
   │ ┌──────────────────────────────────────┐   │
   │ │ ⚠️ Tool Action Requires Approval     │   │
   │ │                                      │   │
   │ │ File: /src/main.py                   │   │
   │ │ Action: Replace text                 │   │
   │ │ ─────────────────────────────────    │   │
   │ │ - def main():                        │   │
   │ │ + import logging                     │   │
   │ │ + def main():                        │   │
   │ │ ─────────────────────────────────    │   │
   │ │                                      │   │
   │ │ ☑ Approve  [selected]                │   │
   │ │ ☐ Reject                             │   │
   │ └──────────────────────────────────────┘   │
   └────────────────┬────────────────────────────┘
                    │
6. RESUME EXECUTION
   ┌────────────────▼────────────────────────────┐
   │ agent.stream(Command(resume={"approve"}))   │
   │ ┌──────────────────────────────────────┐   │
   │ │ ✅ File edited successfully          │   │
   │ │ ┌────────────────────────────────┐   │   │
   │ │ │ src/main.py                    │   │   │
   │ │ │ ─────────────────────────────  │   │   │
   │ │ │ - def main():                  │   │   │
   │ │ │ + import logging               │   │   │
   │ │ │ + logging.basicConfig(...)     │   │   │
   │ │ │ + def main():                  │   │   │
   │ │ └────────────────────────────────┘   │   │
   │ └──────────────────────────────────────┘   │
   │ ┌──────────────────────────────────────┐   │
   │ │ AI: I've added logging to main.py.   │   │
   │ │ The logger is configured to...       │   │
   │ └──────────────────────────────────────┘   │
   └────────────────┬────────────────────────────┘
                    │
7. TOKEN TRACKING
   ┌────────────────▼────────────────────────────┐
   │ token_tracker.add(input_tokens, output_toks)│
   │ Display: /tokens command                    │
   └─────────────────────────────────────────────┘
```

---

## Key Features Summary

### 1. **Persistent Memory**
- Agent stores knowledge in `~/.deepagents/{agent_id}/agent.md`
- Can self-modify instructions based on user feedback
- Memory-first protocol: check `/memories/` before answering

### 2. **Human-in-the-Loop (HITL)**
- Interactive approval for sensitive operations
- Arrow key navigation (up/down, enter)
- Diff preview for file edits
- Auto-approve mode toggle (Ctrl+T)

### 3. **Streaming UI**
- Real-time agent responses
- Tool execution indicators
- Todo list rendering
- Summary panel formatting
- File operation diffs

### 4. **File Mentions**
- `@file.py` syntax to inject file contents
- Autocomplete with case-insensitive matching
- Supports paths with spaces (escaped)

### 5. **Command System**
- Slash commands: `/clear`, `/help`, `/tokens`, `/quit`
- Bash commands: `!ls`, `!git status`
- Regular prompts: sent to agent

### 6. **Token Tracking**
- Baseline calculation (system prompt + agent.md)
- Per-interaction tracking
- Session totals via `/tokens`

### 7. **Multi-Line Input**
- Enter to submit (or apply autocomplete)
- Alt+Enter for newlines
- Ctrl+E to open editor (nano/vim)
- Ctrl+T to toggle auto-approve

### 8. **Agent Management**
- `deepagents list` - show all agents
- `deepagents reset --agent NAME` - reset to default
- `deepagents reset --agent A --target B` - copy from another

---

## Configuration

### Environment Variables

```bash
# Required (at least one)
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# Optional
export ANTHROPIC_MODEL="claude-sonnet-4-5-20250929"  # default
export OPENAI_MODEL="gpt-5-mini"                    # default
export TAVILY_API_KEY="tvly-..."                    # for web search
export EDITOR="nano"                                # for Ctrl+E
```

### Agent Directory Structure

```
~/.deepagents/
├── agent/                  # Default agent
│   └── agent.md           # Agent's self-instructions
├── researcher/            # Custom agent
│   ├── agent.md
│   └── project_notes.md
└── coder/                 # Another custom agent
    └── agent.md
```

### Color Scheme (`config.py`)

```python
COLORS = {
    "primary": "#10b981",   # Green (agent responses)
    "dim": "#6b7280",       # Gray (metadata)
    "user": "#ffffff",      # White (user input)
    "agent": "#10b981",     # Green (agent text)
    "thinking": "#34d399",  # Light green (thinking state)
    "tool": "#fbbf24",      # Amber (tool calls)
}
```

---

## Best Practices

### For Users

1. **Use file mentions**: `@file.py` instead of copy-pasting
2. **Leverage memory**: Tell agent to remember patterns
3. **Auto-approve mode**: Use `Ctrl+T` for trusted workflows
4. **Clear context**: Use `/clear` when switching topics
5. **Check tokens**: Use `/tokens` to monitor usage

### For Developers

1. **Read agent.py first**: Understand middleware stack
2. **Study execution.py**: Master the streaming pattern
3. **Extend tools.py**: Add custom tools as needed
4. **Test HITL**: Verify approval flow works correctly
5. **Monitor memory**: Check `~/.deepagents/` structure

---

## Architecture Strengths

1. **Modularity**: Clean separation (input, execution, rendering)
2. **Extensibility**: Easy to add tools, middleware, commands
3. **User Experience**: Rich UI with diffs, todos, streaming
4. **Safety**: HITL prevents accidental destructive operations
5. **Memory**: Persistent agent instructions enable learning
6. **Performance**: Token tracking and baseline calculation
7. **Flexibility**: OpenAI or Anthropic, auto-approve mode

---

## Conclusion

The DeepAgents CLI is a **production-grade AI coding assistant** that demonstrates:
- Advanced LangGraph patterns (middleware, HITL, streaming)
- Sophisticated terminal UI (Prompt Toolkit, Rich)
- Persistent agent memory and self-modification
- Safe execution with approval gates
- Excellent developer experience

It serves as both a **powerful tool** and a **reference implementation** for building AI-powered CLIs.
