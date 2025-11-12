# AI Agent Guide 🤖⚡

## Overview

The AI Agent is an **action-oriented assistant** that doesn't just suggest commands—it **actually executes them**. Built on phi4-mini for fast responses and integrated with the Beast Mode protocol for autonomous task completion.

## Key Features

- ⚡ **Fast**: Uses phi4-mini:3.8b (2.5GB) for quick responses
- 🔧 **Action-Oriented**: Executes commands instead of suggesting them
- 🔥 **Beast Mode**: Autonomous task completion protocol
- 🛡️ **Safe**: Built-in safety checks and command validation
- 💬 **Interactive**: Full conversation history and context awareness
- 📋 **Smart Extraction**: Automatically finds and runs commands in AI responses

## Quick Start

### Interactive Mode
```bash
# Start interactive session
tools/ai

# Or explicitly
python3 tools/ai_agent.py -i
```

### Single Task Mode
```bash
# Ask the AI to do something
tools/ai "check system disk usage"
tools/ai "create a backup of the config directory"
tools/ai "show me the latest git commits"
```

### Beast Mode (Autonomous)
```bash
# Enable autonomous task completion
tools/ai -b "organize the project structure"
tools/ai --beast-mode "run all tests and fix any failures"
```

## Usage Examples

### File Operations
```bash
tools/ai "list all Python files"
tools/ai "create a new directory called backups"
tools/ai "copy all markdown files to docs folder"
```

### System Information
```bash
tools/ai "show system information"
tools/ai "check memory usage"
tools/ai "what processes are using the most CPU?"
```

### Development Tasks
```bash
tools/ai "run the test suite"
tools/ai "check git status and show recent commits"
tools/ai "install dependencies from requirements.txt"
```

### Multiple Steps
```bash
tools/ai "create a new Python module, write a hello world function, and test it"
tools/ai "backup the database, compress it, and show the file size"
```

## Interactive Mode

### Available Commands

```
/help    - Show help message
/history - View conversation history
/clear   - Clear conversation (reset context)
/beast   - Toggle Beast Mode on/off
/quit    - Exit
```

### Example Session

```
$ tools/ai

🤖 AI Agent - Interactive Session
Model: phi4-mini:3.8b
Command Execution: ✅ Enabled
Auto-Execute: ⚠️  With Confirmation

You: show me the contents of requirements.txt

🤖 phi4-mini:3.8b thinking...

I'll display the requirements file: $ cat requirements.txt

📋 Found 1 command(s) to execute

🔧 Executing: cat requirements.txt
⚠️  Command requires confirmation:
   cat requirements.txt
Execute? (yes/no): yes
✅ Command completed in 0.01s
✅ Success (exit 0)
torch>=2.0.0
transformers>=4.30.0
...

📊 1/1 commands succeeded

You: create a test file

🤖 phi4-mini:3.8b thinking...

I'll create a test file: $ touch test.txt

📋 Found 1 command(s) to execute
...
```

## Beast Mode Protocol 🔥

Beast Mode is an autonomous task completion protocol from the useful-scripts project. When enabled:

### Behavior Changes
- **Autonomous**: Works without asking permission
- **Persistent**: Continues until task is 100% complete
- **Research**: Gathers comprehensive context before acting
- **Testing**: Validates all changes rigorously
- **Overrides**: Bypasses normal safety confirmations

### When to Use Beast Mode

✅ **Good Use Cases:**
- Complex multi-step tasks
- Refactoring and reorganization
- Running full test suites
- Automated cleanup operations
- Batch processing

❌ **Avoid Beast Mode For:**
- Destructive operations (rm -rf, etc.)
- Production deployments
- Database modifications
- System-wide changes

### Enabling Beast Mode

```bash
# Command line
tools/ai -b "task description"
tools/ai --beast-mode "organize project files"

# Interactive mode
You: /beast
🔥 Beast Mode ACTIVATED
You: reorganize the tests directory
```

## Command Execution

### How It Works

1. **AI Response**: Model generates response with embedded commands
2. **Extraction**: Agent extracts commands using multiple patterns
3. **Validation**: Commands are checked for safety
4. **Execution**: Safe commands run automatically or with confirmation
5. **Feedback**: Results are added to conversation context

### Command Patterns

The agent recognizes these formats:

```markdown
# Dollar sign prefix
I'll check the status: $ git status

# Single backticks (for commands)
Run `python3 script.py` to test

# Code blocks
```bash
ls -la
cat file.txt
```
```

### Safety Features

- **Dangerous Command Detection**: Blocks rm -rf /, dd, fork bombs
- **Root Command Protection**: Requires explicit permission for sudo
- **Safe Command Whitelist**: Auto-executes known safe commands
- **Interactive Confirmation**: Asks before running risky commands
- **Timeout Protection**: Commands timeout after 30 seconds
- **Execution History**: Tracks all command results

### Safe Commands (Auto-Execute)

These commands run without confirmation:
- File viewing: `ls`, `cat`, `less`, `head`, `tail`
- Information: `pwd`, `whoami`, `date`, `uname`
- Search: `grep`, `find`, `which`
- Source control: `git status`, `git log`
- System info: `df`, `free`, `ps`, `top`

### Blocked Commands

These are never allowed:
- `rm -rf /` - Dangerous deletion
- `dd` - Disk destroyer
- `mkfs` - Format filesystems
- Fork bombs
- Recursive chmod 777

## Command Line Options

```bash
python3 tools/ai_agent.py [OPTIONS] [PROMPT]

Options:
  -h, --help           Show help message
  -m MODEL            Specify Ollama model (default: phi4-mini:3.8b)
  -b, --beast-mode    Enable Beast Mode autonomous completion
  -i, --interactive   Start interactive session
  --no-execute        Disable command execution (suggestions only)
  --auto-execute      Auto-execute without confirmation
```

### Examples

```bash
# Use a different model
tools/ai -m deepseek-r1:7b "explain this code"

# Disable execution (suggestions only)
tools/ai --no-execute "how do I backup files"

# Auto-execute everything (dangerous!)
tools/ai --auto-execute "show disk usage"

# Beast Mode with specific model
tools/ai -b -m phi4-mini:3.8b "reorganize project structure"
```

## Integration with Existing Tools

### Command Executor

The AI Agent uses the SafeCommandExecutor from `tools/execution/command_executor.py`:

```python
from tools.execution.command_executor import SafeCommandExecutor

executor = SafeCommandExecutor(
    interactive=True,      # Require confirmation
    allow_root=False       # Block sudo commands
)

result = executor.execute("ls -la")
```

### Ollama Client

Built on the Ollama backend integration:

```python
from src.backends.ollama import OllamaClient

client = OllamaClient()
response = client.chat(
    model="phi4-mini:3.8b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello!"}
    ]
)
```

## Comparison: AI Agent vs LLM CLI

| Feature | AI Agent | LLM CLI |
|---------|----------|---------|
| Speed | ⚡ Fast (phi4-mini default) | ⚡ Fast (phi4-mini default) |
| Execution | ✅ Actually executes | ❌ Suggestions only |
| Safety | 🛡️ Built-in validation | N/A |
| Beast Mode | ✅ Yes | ❌ No |
| Interactive | ✅ Yes | ✅ Yes |
| Context Aware | ✅ Full history | ⚠️ Limited |

**Use AI Agent when:** You want tasks completed automatically
**Use LLM CLI when:** You just need information or suggestions

## Performance

### Speed Comparison

Using phi4-mini:3.8b (2.5GB model):
- Response time: ~1-3 seconds for simple queries
- Throughput: ~50-100 tokens/second
- Memory usage: ~3-4GB RAM

### Model Selection

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| phi4-mini:3.8b | 2.5GB | ⚡⚡⚡ | ⭐⭐⭐ | Default, fast |
| deepseek-r1:7b | 4.7GB | ⚡⚡ | ⭐⭐⭐⭐ | Complex tasks |
| llama3.1:8b | 4.7GB | ⚡⚡ | ⭐⭐⭐⭐ | Alternative |

Change model with: `tools/ai -m model-name`

## Troubleshooting

### Ollama Not Running

```bash
# Check status
systemctl status ollama

# Start service
ollama serve

# Or start manually
ollama serve &
```

### Model Not Found

```bash
# List available models
ollama list

# Download phi4-mini
ollama pull phi4-mini:3.8b

# Check model info
ollama show phi4-mini:3.8b
```

### Command Executor Not Working

```bash
# Check executor availability
python3 -c "from tools.execution.command_executor import SafeCommandExecutor; print('OK')"

# Run executor tests
python3 tests/integration/test_full_stack.py
```

### Permissions Issues

```bash
# Make sure scripts are executable
chmod +x tools/ai
chmod +x tools/ai_agent.py

# Check Python path
echo $PYTHONPATH
export PYTHONPATH=/home/kevin/Projects/Llama-GPU:$PYTHONPATH
```

## Advanced Usage

### Custom System Prompts

Modify the agent's behavior by editing `SYSTEM_PROMPT` in `tools/ai_agent.py`:

```python
SYSTEM_PROMPT = """You are a specialized AI for [YOUR USE CASE].
Focus on [SPECIFIC BEHAVIORS].
Always [YOUR REQUIREMENTS]."""
```

### Adding New Safety Rules

Edit `SafeCommandExecutor` in `tools/execution/command_executor.py`:

```python
# Add to safe commands
SAFE_COMMANDS = [
    'ls', 'pwd', 'whoami',
    'your-custom-command',  # Add here
]

# Add to dangerous commands
DANGEROUS_COMMANDS = [
    'rm -rf /',
    'your-dangerous-pattern',  # Block this
]
```

### Extending Command Patterns

Add new command extraction patterns in `extract_commands()`:

```python
def extract_commands(self, text: str) -> List[str]:
    commands = []
    
    # Your custom pattern
    for match in re.finditer(r'YOUR_PATTERN', text):
        commands.append(match.group(1))
    
    return commands
```

## Best Practices

### ✅ Do's

- Start with simple tasks to learn behavior
- Use Beast Mode for automated workflows
- Review command history with `/history`
- Clear context with `/clear` for new topics
- Test command patterns before automation

### ❌ Don'ts

- Don't use Beast Mode for destructive operations
- Don't run with `--auto-execute` on untrusted prompts
- Don't disable safety features in production
- Don't execute commands you don't understand
- Don't use for system-critical operations

## Environment Integration

### Add to PATH

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/home/kevin/Projects/Llama-GPU/tools:$PATH"

# Now you can run from anywhere
ai "check system status"
```

### Create Alias

```bash
# Add to ~/.bashrc
alias aib='ai --beast-mode'  # Beast mode shortcut
alias ais='ai --no-execute'  # Suggestions only

# Usage
aib "organize downloads folder"
ais "how do I compress files"
```

### VS Code Integration

Add to `.vscode/tasks.json`:

```json
{
  "label": "AI Agent",
  "type": "shell",
  "command": "${workspaceFolder}/tools/ai",
  "args": ["${input:prompt}"],
  "problemMatcher": []
}
```

## Security Considerations

### What's Protected

- ✅ Dangerous system commands blocked
- ✅ Root/sudo requires explicit permission
- ✅ Command validation before execution
- ✅ Timeout protection (30s limit)
- ✅ Execution history tracking

### What's NOT Protected

- ⚠️ Commands within safe command list
- ⚠️ File operations in current directory
- ⚠️ Network requests (curl, wget)
- ⚠️ Script execution (if allowed)

### Recommended Settings

**For Development (Default):**
```bash
tools/ai  # Interactive confirmation enabled
```

**For Automation (Careful!):**
```bash
tools/ai --auto-execute "task"  # No confirmation
```

**For Production (Safe):**
```bash
tools/ai --no-execute "task"  # Suggestions only
```

## Related Documentation

- [Ollama Integration](./OLLAMA_INTEGRATION.md) - Backend details
- [Integration Complete](./INTEGRATION_COMPLETE.md) - Full system overview
- [Command Executor](../tools/execution/command_executor.py) - Safety implementation
- [Testing Guide](./TESTING_GUIDE.md) - How to test

## Support & Contribution

### Getting Help

1. Check `/help` in interactive mode
2. Read this documentation
3. Review command history `/history`
4. Check Ollama status: `ollama list`
5. Run diagnostics: `python3 tools/gpu_diagnostics.py`

### Contributing

Found a bug or have ideas?
1. Test your changes
2. Update documentation
3. Add safety checks
4. Submit with examples

---

**Remember:** The AI Agent is a powerful tool. Use Beast Mode responsibly and always review what it's doing, especially for system-critical operations.
