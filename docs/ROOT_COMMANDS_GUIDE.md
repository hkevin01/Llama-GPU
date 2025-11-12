# Root Commands & Sudo Handling 🔒

## Important Safety Feature

The AI Assistant **CANNOT** execute commands that require root/sudo privileges. This is a security feature to prevent accidental system damage.

## What's Blocked

The following commands are automatically blocked:

### Package Management
- `apt`, `apt-get`, `aptitude`
- `yum`, `dnf`, `zypper`
- `pacman`
- System updates and package installs

### System Services
- `systemctl` (start, stop, restart services)
- `service` (legacy service management)

### User Management
- `useradd`, `userdel`, `usermod`
- `passwd` (changing other users' passwords)
- `groupadd`, `groupdel`

### Disk Operations
- `mount`, `umount`
- `fdisk`, `parted`, `gparted`
- `mkfs` (formatting filesystems)

### Other Dangerous Commands
- Anything prefixed with `sudo`
- `dd` (disk destroyer)
- `rm -rf /` (system destruction)
- Fork bombs and similar

## What the AI Will Do

When you ask for a root operation, the AI will:

1. ✅ **Explain** what needs to be done
2. ✅ **Provide** the exact command
3. ✅ **Tell you** to run it manually with sudo
4. ❌ **NOT execute** the command itself

### Example Interaction

**You:** "update the system"

**AI Response:**
```
I cannot execute system updates as they require sudo privileges.

To update your system, run these commands in your terminal:

$ sudo apt update
$ sudo apt upgrade -y

This will:
1. Update package lists
2. Install available updates

Would you like me to help with something else?
```

## What the AI CAN Do

The AI can execute these without sudo:

### File Operations ✅
```bash
ls, cat, grep, find, mkdir, touch
cp, mv, rm (in user directories)
head, tail, less, more
```

### System Information ✅
```bash
df -h          # Disk usage
free -h        # Memory usage
ps aux         # Process list
top, htop      # System monitor
whoami         # Current user
pwd            # Current directory
uname -a       # System info
uptime         # System uptime
```

### Development ✅
```bash
python3 script.py
git status, git log, git diff
npm run (without install)
pip install --user package  # User-level install
```

### Network ✅
```bash
curl https://example.com
wget https://example.com/file
ping google.com
netstat -tuln  # Network connections
```

## Workarounds

### Package Installation

**Instead of:** AI installing packages
**Do this:**
1. Ask AI what package you need
2. AI provides the command
3. You run it with sudo

```bash
# AI tells you:
"You need to install package X"
"Run: sudo apt install package-name"

# You run:
$ sudo apt install package-name
```

### Service Management

**Instead of:** AI managing services
**Do this:**
1. Ask AI about the service
2. AI provides status/management commands
3. You run them with sudo

```bash
# AI tells you:
"To restart nginx, run:"
"sudo systemctl restart nginx"

# You run:
$ sudo systemctl restart nginx
```

### User-Level Alternatives

Some operations have user-level alternatives:

| Root Command | User Alternative |
|--------------|------------------|
| `apt install pkg` | `pip install --user pkg` (for Python) |
| `systemctl --user` | User services (if supported) |
| `npm install -g` | `npm install` (local to project) |

## Beast Mode Behavior

Even in **Beast Mode** (autonomous execution), the AI will:
- ❌ **NOT** attempt sudo commands
- ✅ **Explain** what needs root access
- ✅ **Provide** commands for manual execution
- ✅ **Continue** with non-root tasks

Beast Mode respects security boundaries!

## Safety Design

This restriction is intentional for:

### Security 🔒
- Prevents accidental system damage
- Protects against malicious commands
- Limits blast radius of errors

### Control 🎛️
- You decide what runs as root
- Review commands before execution
- Maintain system integrity

### Best Practices ✅
- Principle of least privilege
- Explicit authorization for sensitive operations
- Audit trail (you see and approve sudo commands)

## How It Works

The `SafeCommandExecutor` checks commands:

```python
# Checks for root commands
ROOT_COMMANDS = [
    'apt', 'apt-get', 'systemctl', 'service',
    'useradd', 'userdel', 'passwd',
    'mount', 'umount', 'fdisk', 'parted'
]

# Checks for sudo prefix
if command.startswith('sudo'):
    return "blocked"
    
# Validates before execution
validate_command(cmd)
```

## Configuration

### Enable Root (Not Recommended)

If you absolutely need it:

```python
# In ai_assistant_app.py or ai_agent.py
self.executor = SafeCommandExecutor(
    interactive=True,
    allow_root=True  # ⚠️ DANGEROUS!
)
```

**WARNING:** Only enable if you:
- Understand the risks
- Trust the AI completely
- Are in a sandboxed environment
- Know how to recover from system damage

### Customize Blocked Commands

Edit `tools/execution/command_executor.py`:

```python
ROOT_COMMANDS = [
    'apt', 'systemctl',
    'your-custom-command',  # Add here
]
```

## Examples

### Good: Information Gathering
```
You: "check disk space"
AI: $ df -h
✅ Executes successfully
```

### Good: File Operations
```
You: "list recent files"
AI: $ ls -lt | head -10
✅ Executes successfully
```

### Blocked: Package Install
```
You: "install nodejs"
AI: "I cannot install packages. Run: sudo apt install nodejs"
❌ Does not execute
```

### Blocked: Service Restart
```
You: "restart nginx"
AI: "I cannot manage services. Run: sudo systemctl restart nginx"
❌ Does not execute
```

## Testing

Check if a command will work:

```bash
# Safe command - will work
tools/ai "show disk usage"

# Root command - will explain but not execute
tools/ai "install python package"
```

## FAQ

**Q: Why can't the AI use sudo?**
A: Security. Your system is protected from accidental damage.

**Q: Can I enable sudo in Beast Mode?**
A: No. Even Beast Mode respects security boundaries.

**Q: What if I need to update packages?**
A: AI provides the command, you run it manually with sudo.

**Q: Is this a bug?**
A: No, it's a feature! It protects your system.

**Q: Can I disable this?**
A: Yes, but **NOT recommended**. Edit the executor configuration.

## Summary

✅ **Good:** AI executes safe user-level commands
❌ **Blocked:** AI cannot use sudo/root
💡 **Solution:** AI explains and you run sudo commands manually

**This keeps your system safe while still being helpful!**

---

**Remember:** If the AI says it can't run something with sudo, that's the safety feature working correctly!
