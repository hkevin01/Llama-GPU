# Direct Execution - Test Guide 🧪

**Quick test checklist for the new direct execution feature**

---

## Before Testing

### 1. Relaunch the App

**Important**: Changes are already in the code, just restart:

```bash
# Method 1: From applications menu
Super Key → "Llama GPU" → Click

# Method 2: From terminal
./bin/llama-assistant

# Method 3: Kill and restart
pkill -f ai_assistant_app
./bin/llama-assistant
```

---

## Test Cases

### ✅ Test 1: Ubuntu Version

**Say this:**
```
what is my ubuntu version
```

**Expected behavior:**
```
🔧 Executing: lsb_release -a 2>/dev/null || cat /etc/os-release
✅ Distributor ID: Ubuntu
Description:    Ubuntu 24.04.3 LTS
Release:        24.04
Codename:       noble
```

**Variations to test:**
- "which ubuntu version am i running"
- "show me the os version"
- "tell me my linux version"

---

### ✅ Test 2: Disk Space

**Say this:**
```
how much disk space
```

**Expected behavior:**
```
🔧 Executing: df -h
✅ Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  458G  123G  312G  29% /
tmpfs           3.2G  2.4M  3.2G   1% /run
...
```

**Variations to test:**
- "check disk space"
- "show storage usage"
- "how much space do i have"

---

### ✅ Test 3: Memory Usage

**Say this:**
```
show memory usage
```

**Expected behavior:**
```
🔧 Executing: free -h
✅               total        used        free      shared
Mem:           32Gi        12Gi        18Gi        1.2Gi
Swap:          8.0Gi          0B        8.0Gi
```

**Variations to test:**
- "how much ram"
- "check memory"
- "what's my memory usage"

---

### ✅ Test 4: Who Am I

**Say this:**
```
who am i
```

**Expected behavior:**
```
🔧 Executing: whoami
✅ kevin
```

**Variations to test:**
- "what's my username"
- "what user am i"

---

### ✅ Test 5: IP Address

**Say this:**
```
what's my ip address
```

**Expected behavior:**
```
🔧 Executing: ip addr show | grep inet
✅ inet 127.0.0.1/8 scope host lo
    inet 192.168.1.100/24 brd 192.168.1.255 scope global eth0
```

**Variations to test:**
- "show my ip"
- "get my ip address"

---

### ✅ Test 6: GPU Info

**Say this:**
```
show gpu info
```

**Expected behavior:**
```
🔧 Executing: lspci | grep -i vga
✅ 01:00.0 VGA compatible controller: Advanced Micro Devices...
```

**Variations to test:**
- "list graphics cards"
- "what gpu do i have"

---

### ✅ Test 7: Running Processes

**Say this:**
```
show running processes
```

**Expected behavior:**
```
🔧 Executing: ps aux --sort=-%mem | head -20
✅ USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1 168624 11716 ?        Ss   Nov12   0:15 /sbin/init
...
```

---

### ✅ Test 8: Kernel Version

**Say this:**
```
what kernel am i running
```

**Expected behavior:**
```
🔧 Executing: uname -r
✅ 6.8.0-49-generic
```

---

### ✅ Test 9: Internet Connection

**Say this:**
```
check internet connection
```

**Expected behavior:**
```
🔧 Executing: ping -c 4 8.8.8.8
✅ PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=12.5 ms
...
--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss
```

---

### ✅ Test 10: Complex AI Query (Fallback Test)

**Say this:**
```
tell me about quantum computing
```

**Expected behavior:**
```
AI: Quantum computing is a type of computation that harnesses...
(Full AI explanation, NOT a command execution)
```

**Purpose**: Verify that non-system queries still go to the AI normally.

---

## What to Look For

### ✅ **SUCCESS** looks like:

1. **Instant execution**: Command runs immediately, no delay
2. **Clear formatting**: 
   - `�� Executing: <command>` appears first
   - `✅ <output>` shows results
3. **No instructions**: AI doesn't say "you need to run..."
4. **Correct output**: Results match what you'd get in terminal

### ❌ **FAILURE** looks like:

1. **Instructions instead of execution**:
   ```
   AI: You need to run the command lsb_release -a to check...
   ```

2. **No execution icon**: Missing `🔧 Executing:` indicator

3. **Error message**:
   ```
   ❌ Command failed: <error>
   ```
   (Check error, may be legitimate like command not found)

4. **AI confusion**: 
   ```
   AI: I'm not sure what you mean by...
   ```
   (Pattern may not be matching)

---

## Troubleshooting

### Problem: Commands Not Executing

**Solution 1**: Check if app restarted
```bash
# Kill old process
pkill -f ai_assistant_app

# Start fresh
./bin/llama-assistant
```

**Solution 2**: Check syntax
```bash
# Verify code has no errors
python3 -m py_compile tools/gui/ai_assistant_app.py
```

### Problem: AI Still Giving Instructions

**Possible causes:**
1. Query doesn't match any pattern
2. Old AI response cached
3. App not restarted

**Solution**:
```bash
# Clear history and restart
rm ~/.config/llama-gpu-assistant/history.json
./bin/llama-assistant
```

### Problem: Command Shows Error

**Expected** if command actually fails:
```
❌ bash: sensors: command not found
```

This is correct behavior - the command executed but the tool isn't installed.

**To fix**: Install missing tool:
```bash
sudo apt install lm-sensors
```

---

## Pattern Matching Debug

Test patterns in terminal:

```bash
cd /home/kevin/Projects/Llama-GPU

python3 << 'PYEOF'
import re

# Your test queries
queries = [
    "what is my ubuntu version",
    "how much disk space",
    "show memory usage",
    "who am i",
    "what's my ip",
]

# Patterns from code
patterns = {
    r'(?:what|which|show|tell|get).*(?:ubuntu|os|linux|system).*version': 'lsb_release -a',
    r'(?:how much|what|show|check).*(?:disk|storage|space)': 'df -h',
    r'(?:how much|what|show|check|usage).*(?:memory|ram)': 'free -h',
    r'(?:what|who).*(?:user|logged in|am i)': 'whoami',
    r'(?:what|show|get).*(?:ip|address)': 'ip addr show | grep inet',
}

for q in queries:
    matched = False
    for pattern, cmd in patterns.items():
        if re.search(pattern, q.lower()):
            print(f"✅ '{q}' → {cmd}")
            matched = True
            break
    if not matched:
        print(f"❌ '{q}' → NO MATCH")
PYEOF
```

---

## Success Criteria

**Feature is working correctly if:**

- ✅ At least 8/9 system queries execute immediately
- ✅ Results show with `🔧` and `✅` icons
- ✅ No "you need to run..." instructions
- ✅ Complex AI queries still go to AI (Test 10)
- ✅ Execution time < 2 seconds for simple commands
- ✅ History saves successfully (check History menu)

---

## Report Issues

If you find problems, gather:

1. **Query used**: Exact text you typed
2. **Expected**: What should have happened
3. **Actual**: What actually happened
4. **Logs**: Any terminal output from `./bin/llama-assistant`

Then report in GitHub Issues or conversation history.

---

**Status**: Ready for testing! 🚀  
**Next**: Run through all test cases and report back
