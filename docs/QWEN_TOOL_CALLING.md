# Qwen3 Native Tool Calling for Ubuntu

This document describes the native Ollama tool-calling support added to the Llama-GPU Assistant for reliable command execution with Qwen3.

## Overview

The Llama-GPU Assistant now supports **native Ollama tool-calling** which provides more reliable command execution than the previous text-parsing approach. Qwen3 models have built-in support for tool calling, making it the recommended approach.

## Quick Start

### Using the Tool Agent directly

```bash
# Single command
python3 tools/tool_agent.py "List files in the current directory"

# Interactive mode
python3 tools/tool_agent.py
```

### Using the AI Agent with native tools

```bash
# With native tool-calling (recommended for Qwen3)
python3 tools/ai_agent.py -t "Show system information"

# Interactive mode with tools
python3 tools/ai_agent.py -t -i
```

## Available Tools

The following tools are available to the agent:

| Tool | Description |
|------|-------------|
| `run_command` | Execute shell commands (ls, cat, grep, python3, etc.) |
| `read_file` | Read file contents |
| `write_file` | Write content to files |
| `list_directory` | List directory contents |

## How It Works

1. **User Request**: You ask the agent to perform an action
2. **Tool Selection**: Qwen3 decides which tool(s) to use
3. **Execution**: The agent executes the selected tool(s)
4. **Response**: The agent formats the results as a helpful response

Example flow:
```
User: "List Python files in the tools folder"
→ Qwen3 calls: run_command({"command": "ls tools/*.py"})
→ Agent executes the command
→ Agent formats: "Here are the Python files: ai_agent.py, tool_agent.py, ..."
```

## Command Line Options

### tool_agent.py
```
python3 tools/tool_agent.py [options] [prompt]

Options:
  -m, --model MODEL    Ollama model (default: qwen3:4b)
  -v, --verbose        Verbose output
```

### ai_agent.py  
```
python3 tools/ai_agent.py [options] [prompt]

Options:
  -t, --native-tools   Use native Ollama tool-calling (recommended)
  -m, --model MODEL    Ollama model (default: qwen3:4b)
  -b, --beast-mode     Autonomous task completion
  -i, --interactive    Interactive session
```

## Safety Features

- Dangerous commands are blocked (rm -rf /, mkfs, etc.)
- Command timeout of 30 seconds
- All command executions are logged

## Model Requirements

- Qwen3:4b or larger (supports tools)
- Other Ollama models with tool support

Check if your model supports tools:
```bash
curl http://localhost:11434/api/show -d '{"model": "qwen3:4b"}' | jq '.capabilities'
```

## Files

- `tools/tool_agent.py` - Native tool-calling agent
- `tools/ai_agent.py` - Original agent with `-t` flag for native tools
- `src/backends/ollama/ollama_client.py` - Updated with tool-calling support
