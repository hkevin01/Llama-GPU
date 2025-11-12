# AI Agent Quick Start ⚡

## TL;DR

```bash
# Start AI that actually DOES things
tools/ai

# Ask it to do something
You: create a backup of my scripts
You: show me disk usage
You: run the test suite

# Beast Mode (autonomous)
tools/ai -b "organize this messy directory"
```

## 3 Core Modes

### 1️⃣ Interactive (Default)
```bash
tools/ai
```
- Chat with AI
- It executes commands after confirmation
- Use `/beast` to toggle autonomous mode

### 2️⃣ Single Task
```bash
tools/ai "check git status and show last 5 commits"
```
- One-off task
- AI does it immediately
- Shows results and exits

### 3️⃣ Beast Mode 🔥
```bash
tools/ai -b "run all tests and fix failures"
```
- **Autonomous** - no permission needed
- **Persistent** - works until 100% complete
- **Powerful** - use carefully!

## Command Cheat Sheet

### Interactive Commands
```
/help     - Show help
/history  - View conversation
/clear    - Reset context
/beast    - Toggle Beast Mode
/quit     - Exit
```

### CLI Options
```bash
-i, --interactive    # Start interactive mode
-b, --beast-mode     # Enable autonomous mode
-m MODEL             # Use specific model
--no-execute         # Suggestions only
--auto-execute       # Skip confirmations
```

## Quick Examples

### File Operations
```bash
tools/ai "list all Python files larger than 1MB"
tools/ai "create a backup directory and copy configs"
tools/ai "find TODO comments in the codebase"
```

### System Tasks
```bash
tools/ai "show system info and disk usage"
tools/ai "what's using the most memory?"
tools/ai "check if port 8080 is in use"
```

### Development
```bash
tools/ai "run pytest on the tests directory"
tools/ai "show git diff of modified files"
tools/ai "install missing dependencies"
```

### Multi-Step Tasks
```bash
tools/ai "create a test file, write a function, and run it"
tools/ai "backup configs, compress them, show the size"
tools/ai "check system health: disk, memory, and load"
```

## Safety Features

✅ **Safe Commands** - Auto-executes without asking
- `ls`, `cat`, `pwd`, `whoami`
- `git status`, `git log`
- `df`, `free`, `ps`, `top`

⚠️ **Requires Confirmation**
- File modifications
- Network operations
- Script execution

❌ **Blocked**
- `rm -rf /`
- `dd` operations
- Fork bombs
- `sudo` (unless explicitly enabled)

## Tips & Tricks

### Speed It Up
```bash
# Use phi4-mini (default, fastest)
tools/ai "quick task"

# Use deepseek for complex reasoning
tools/ai -m deepseek-r1:7b "complex analysis"
```

### Batch Operations
```bash
# Beast Mode for automation
tools/ai -b "organize all docs, run tests, update README"
```

### Context Aware
```bash
# Interactive mode remembers conversation
tools/ai
You: what files are in the current directory?
You: now compress the largest one
You: and show me the result
```

### Skip Confirmations (Careful!)
```bash
# Auto-execute everything
tools/ai --auto-execute "safe read-only task"
```

## Common Issues

### "Ollama service not running"
```bash
ollama serve
# Or start in background
ollama serve &
```

### "Model not found"
```bash
ollama pull phi4-mini:3.8b
```

### "Command executor not available"
```bash
# Check Python path
cd /home/kevin/Projects/Llama-GPU
python3 tools/ai_agent.py
```

## Model Selection

| Model | Speed | Quality | Use When |
|-------|-------|---------|----------|
| **phi4-mini:3.8b** | ⚡⚡⚡ | ⭐⭐⭐ | Default, quick tasks |
| **deepseek-r1:7b** | ⚡⚡ | ⭐⭐⭐⭐ | Complex reasoning |

Change with: `tools/ai -m model-name`

## Comparison

### Old Way (LLM CLI)
```bash
$ tools/llm_cli.py "list files"
🤖: You can list files with: ls -la
# YOU have to run: ls -la
```

### New Way (AI Agent)
```bash
$ tools/ai "list files"
🤖: I'll show you the files: $ ls -la

📋 Found 1 command(s) to execute
🔧 Executing: ls -la
✅ Success
[actual file listing shown]
```

**The AI actually DOES it!**

## When to Use What

| Situation | Use | Command |
|-----------|-----|---------|
| Quick info | AI Agent | `tools/ai "question"` |
| Conversation | AI Agent | `tools/ai` |
| Just chatting | LLM CLI | `tools/llm_cli.py -i` |
| Complex task | Beast Mode | `tools/ai -b "task"` |
| Suggestions only | LLM CLI | `tools/llm_cli.py` |

## Next Steps

1. **Try it**: `tools/ai`
2. **Read full guide**: [AI_AGENT_GUIDE.md](./AI_AGENT_GUIDE.md)
3. **Learn safety**: Review command executor code
4. **Customize**: Edit system prompts

---

**Quick Help**: `tools/ai /help` or `tools/ai --help`

**Full Docs**: [AI_AGENT_GUIDE.md](./AI_AGENT_GUIDE.md)
