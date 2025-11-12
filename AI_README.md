# AI Assistant - Quick Reference ��

## TL;DR - Just Want To Use It?

```bash
# Fast AI that actually does things
tools/ai "check disk space"

# Interactive mode
tools/ai

# Autonomous Beast Mode
tools/ai -b "organize and clean up"

# Desktop app (after install)
./install-desktop-app.sh
```

## What Is This?

An **action-oriented AI assistant** that:
- ⚡ Responds quickly (phi4-mini, 1-3s)
- 🔧 Actually executes commands (doesn't just suggest)
- 🔥 Works autonomously (Beast Mode)
- 🖥️ Runs as native Ubuntu app (GTK3 + system tray)
- 🛡️ Validates safety (blocks dangerous commands)

## Installation

### CLI (Already Installed)
```bash
# Just use it
tools/ai "your task"
```

### Desktop App
```bash
# Run installer
./install-desktop-app.sh

# Launch from menu
# Press Super → type "AI Assistant"
```

## Usage

### CLI Examples
```bash
# Single task
tools/ai "show system information"

# Interactive session
tools/ai -i

# Beast Mode (autonomous)
tools/ai -b "run tests and fix issues"

# Different model
tools/ai -m deepseek-r1:7b "complex analysis"
```

### Desktop App
1. Click system tray icon
2. Select "Open Chat"
3. Type your request
4. AI responds and executes automatically

## Documentation

| Doc | Purpose | Location |
|-----|---------|----------|
| 📖 Quick Start | TL;DR | [AI_AGENT_QUICKSTART.md](docs/AI_AGENT_QUICKSTART.md) |
| 📚 Full Guide | Complete reference | [AI_AGENT_GUIDE.md](docs/AI_AGENT_GUIDE.md) |
| 🖥️ Desktop App | GUI usage | [DESKTOP_APP_GUIDE.md](docs/DESKTOP_APP_GUIDE.md) |
| 📋 Summary | What changed | [AI_UPGRADE_COMPLETE.md](docs/AI_UPGRADE_COMPLETE.md) |
| ✅ Status | Checklist | [AI_UPGRADE_STATUS.md](AI_UPGRADE_STATUS.md) |
| 📁 Manifest | All files | [AI_UPGRADE_MANIFEST.md](AI_UPGRADE_MANIFEST.md) |

## Key Features

### Speed
- **phi4-mini:3.8b** (default): 1-3 second responses
- **deepseek-r1:7b** (optional): Better reasoning

### Execution
- Automatically extracts commands from AI responses
- Runs them with safety validation
- Shows output in real-time

### Safety
- ✅ Safe commands auto-execute (ls, cat, ps, etc.)
- ⚠️ Risky commands need confirmation
- ❌ Dangerous commands blocked (rm -rf /, dd, etc.)

### Beast Mode 🔥
- Toggle in CLI: `tools/ai -b "task"`
- Toggle in GUI: Checkbox in top-right
- Autonomous execution without confirmations
- Works until 100% complete

## Troubleshooting

### "Ollama not running"
```bash
ollama serve
```

### "Model not found"
```bash
ollama pull phi4-mini:3.8b
```

### Desktop app won't start
```bash
./install-desktop-app.sh
```

## File Locations

```
Llama-GPU/
├── tools/
│   ├── ai                      # Quick launcher
│   ├── ai_agent.py             # Main CLI
│   └── gui/
│       └── ai_assistant_app.py # Desktop app
├── docs/
│   ├── AI_AGENT_GUIDE.md       # Full guide
│   ├── AI_AGENT_QUICKSTART.md  # Quick ref
│   └── DESKTOP_APP_GUIDE.md    # GUI guide
├── install-desktop-app.sh      # Installer
└── ai-assistant.desktop        # Desktop entry
```

## Comparison

### Before (LLM CLI)
```
You: "list files"
AI: "You can use: ls -la"
[YOU manually run: ls -la]
```

### After (AI Agent)
```
You: "list files"
AI: $ ls -la
[Executes automatically]
[Shows output]
```

## Quick Commands

```bash
# Help
tools/ai --help

# Status
tools/ai --status # (if implemented)

# Interactive with history
tools/ai -i
/help     # Show commands
/history  # View conversation
/beast    # Toggle Beast Mode
/quit     # Exit
```

## Models

| Model | Speed | Quality | Use When |
|-------|-------|---------|----------|
| phi4-mini:3.8b | ⚡⚡⚡ | ⭐⭐⭐ | Quick tasks (default) |
| deepseek-r1:7b | ⚡⚡ | ⭐⭐⭐⭐ | Complex reasoning |

## Support

1. Check docs: `docs/AI_AGENT_QUICKSTART.md`
2. Verify Ollama: `ollama list`
3. Test CLI: `tools/ai "hello"`
4. Read full guide: `docs/AI_AGENT_GUIDE.md`

## Credits

- **Llama-GPU** project
- **useful-scripts** (Beast Mode protocol)
- **rocm-patch** (GPU detection)
- **Microsoft phi4-mini** (AI model)
- **Ollama** (LLM backend)

---

**Start here**: `tools/ai "your first task"`

**Full docs**: [AI_AGENT_GUIDE.md](docs/AI_AGENT_GUIDE.md)
