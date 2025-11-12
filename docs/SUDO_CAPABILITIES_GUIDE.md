# Sudo Capabilities Guide

## Overview

The AI Agent now has **full sudo capabilities** using the industry-standard `pexpect` library for password handling and interactive command execution.

## What's New

### ✅ Sudo Command Execution

The AI can now execute sudo commands including:
- **Package Management**: `apt update`, `apt install`, `apt upgrade`
- **System Control**: `systemctl start/stop/restart/status`
- **Service Management**: `service nginx restart`
- **User Management**: `useradd`, `usermod`, `passwd`
- **System Operations**: `mount`, `umount`, and more

### 🔐 Security Features

1. **Password Protection**
   - Password prompted securely using `getpass`
   - Password cached per session (optional)
   - Never stored on disk

2. **Command Validation**
   - Extremely dangerous commands BLOCKED (rm -rf /, mkfs, fork bombs)
   - High-risk commands require explicit confirmation
   - All sudo commands logged

3. **User Confirmation**
   - Regular mode: Confirms before every sudo command
   - Beast Mode: Skips confirmation (use with caution)
   - High-risk commands ALWAYS require explicit confirmation

## Usage

### CLI Agent

```bash
# Simple sudo command
./tools/ai "update system packages"

# High-risk command (will prompt for extra confirmation)
./tools/ai "format disk /dev/sdb"

# Beast Mode (skips regular confirmations, but not high-risk)
./tools/ai --beast-mode "install nginx"
```

### Desktop App

1. Launch the app from system tray
2. Type your request: "update system packages"
3. AI will suggest: `$ sudo apt update && sudo apt upgrade`
4. Command will prompt for:
   - Sudo password (first time)
   - Confirmation to execute
5. Progress shown in chat window

### Direct Sudo Executor

```bash
# Test sudo executor directly
python3 tools/execution/sudo_executor.py sudo apt update

# With password (skip prompt)
python3 tools/execution/sudo_executor.py --password yourpass sudo systemctl status nginx

# Skip confirmation
python3 tools/execution/sudo_executor.py --no-confirm sudo ls /root
```

## Architecture

### Components

1. **SudoExecutor** (`tools/execution/sudo_executor.py`)
   - Main sudo handler using pexpect
   - Password management
   - Command validation
   - Safety checks

2. **AIAgent** (`tools/ai_agent.py`)
   - Integrates SudoExecutor
   - Extracts sudo commands
   - Routes to appropriate executor

3. **Desktop App** (`tools/gui/ai_assistant_app.py`)
   - GTK3 UI with sudo support
   - Threaded execution (non-blocking)
   - Visual feedback

### Execution Flow

```
User Request
    ↓
AI generates command
    ↓
Command extraction ($ prefix)
    ↓
Check if needs sudo → YES → SudoExecutor
    │                           ↓
    │                    Safety validation
    │                           ↓
    │                    Password prompt (cached)
    │                           ↓
    │                    User confirmation
    │                           ↓
    │                    pexpect.spawn()
    │                           ↓
    │                    Execute with sudo
    │
    NO → SafeCommandExecutor
         ↓
    Execute normally
```

## Safety Mechanisms

### Never Allowed

These commands are **ALWAYS BLOCKED**:
- `rm -rf /` or `rm -rf /*`
- `dd if=/dev/zero of=/dev/sda`
- `mkfs.*` (format commands)
- `:(){ :|:& };:` (fork bomb)
- `chmod -R 777 /`
- `chown -R root /`

### High-Risk (Extra Confirmation)

These commands require typing "YES I UNDERSTAND":
- `rm -rf` (recursive force delete)
- `dd` (disk operations)
- `fdisk`, `parted` (partition editing)
- `format` commands

### Regular Sudo

All other sudo commands require:
1. Password (first time or cached)
2. Confirmation prompt (unless Beast Mode)

## Examples

### System Updates

```bash
./tools/ai "update my system"
```

Output:
```
🤖 phi4-mini:3.8b thinking...

I'll update your system packages:
$ sudo apt update && sudo apt upgrade -y

📋 Found 1 command(s) to execute
🔐 Executing sudo command: sudo apt update && sudo apt upgrade -y

🔐 Sudo command:
   sudo apt update && sudo apt upgrade -y
   Execute? (yes/no): yes

Enter sudo password: ****

🔧 Executing: sudo apt update && sudo apt upgrade -y
Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease
...
✅ Command completed successfully (exit 0)
```

### Install Software

```bash
./tools/ai "install docker"
```

AI generates:
```
$ sudo apt install docker.io -y
$ sudo systemctl start docker
$ sudo systemctl enable docker
```

Each command prompts for confirmation.

### Service Management

```bash
./tools/ai "restart nginx"
```

AI generates:
```
$ sudo systemctl restart nginx
$ sudo systemctl status nginx
```

### Beast Mode Example

```bash
./tools/ai --beast-mode "setup development environment"
```

AI autonomously:
1. ✅ `sudo apt update` (confirmed once)
2. ✅ `sudo apt install build-essential git python3-pip` (no confirmation)
3. ✅ `git clone ...` (regular command)
4. ✅ `pip3 install ...` (regular command)
5. ✅ Reports completion

## Configuration

### Password Caching

```python
# Enable password caching (default)
sudo_executor = SudoExecutor(cache_password=True)

# Disable (prompt every time)
sudo_executor = SudoExecutor(cache_password=False)

# Pre-set password (not recommended for security)
sudo_executor = SudoExecutor(password="yourpassword")
```

### Timeout

```python
# Set command timeout (default 300s = 5 minutes)
sudo_executor = SudoExecutor(timeout=600)  # 10 minutes
```

### Confirmation

```python
# Execute with confirmation (default)
result = sudo_executor.execute("sudo apt update", confirm=True)

# Skip confirmation (use carefully)
result = sudo_executor.execute("sudo apt update", confirm=False)
```

## Troubleshooting

### Password Incorrect

```
❌ Sudo verification failed: password incorrect
```

**Solution**: Re-enter password when prompted. Password cache is cleared after failed attempt.

### Command Blocked

```
❌ BLOCKED: Extremely dangerous command detected!
```

**Solution**: This is intentional. Don't run these commands. They can destroy your system.

### Timeout

```
❌ Command timed out after 300s
```

**Solution**: Increase timeout for long-running commands:
```python
sudo_executor = SudoExecutor(timeout=1800)  # 30 minutes
```

### Permission Denied (Not in sudoers)

```
user is not in the sudoers file
```

**Solution**: Add user to sudo group:
```bash
# As root or another sudo user
usermod -aG sudo username
```

Log out and back in for changes to take effect.

## Security Best Practices

### 1. Use Password Caching Carefully

✅ **Safe**: Cache for single session, clear on exit
❌ **Risky**: Store password in environment variables or config files

### 2. Review Commands Before Execution

Always check what the AI suggests before confirming, especially:
- File deletions (`rm`)
- System modifications (`systemctl`, `service`)
- Disk operations (`dd`, `fdisk`)

### 3. Use Beast Mode Sparingly

Beast Mode skips confirmations but NOT safety checks. Use only for:
- Trusted automated tasks
- Batch operations you understand
- Development environments (not production)

### 4. Monitor Sudo Logs

System logs track all sudo usage:
```bash
# View recent sudo activity
sudo grep -i sudo /var/log/auth.log

# Watch in real-time
sudo tail -f /var/log/auth.log | grep sudo
```

### 5. Principle of Least Privilege

Only run commands that need sudo with sudo. Regular commands don't need elevated privileges.

## Technical Details

### pexpect Integration

The sudo executor uses `pexpect` for interactive command handling:

```python
import pexpect

# Spawn command with sudo
child = pexpect.spawn('sudo apt update')

# Wait for password prompt
child.expect('[Pp]assword.*:')

# Send password
child.sendline(password)

# Read output line by line
while True:
    line = child.readline()
    if not line:
        break
    print(line.decode())

# Wait for completion
child.close()
exit_code = child.exitstatus
```

### Password Security

- Uses `getpass.getpass()` for secure password input (no echo)
- Password stored in memory only (never disk)
- Cleared on application exit
- Optional caching per session

### Command Validation

Safety checks happen BEFORE execution:

1. **Parse command**: Extract base command and arguments
2. **Check NEVER_ALLOW list**: Block extremely dangerous commands
3. **Check HIGH_RISK list**: Require extra confirmation
4. **Validate syntax**: Ensure command is well-formed
5. **Execute with pexpect**: Handle password and output

## API Reference

### SudoExecutor

```python
class SudoExecutor:
    def __init__(self,
                 password: Optional[str] = None,
                 cache_password: bool = True,
                 timeout: int = 300):
        """Initialize sudo executor."""
    
    def verify_sudo_access(self) -> bool:
        """Verify user has sudo access."""
    
    def execute_sudo(self,
                     command: str,
                     confirm: bool = True,
                     use_sudo: bool = True) -> SudoResult:
        """Execute command with sudo."""
    
    def execute(self, command: str, confirm: bool = True) -> SudoResult:
        """Execute command (auto-detects sudo need)."""
```

### SudoResult

```python
@dataclass
class SudoResult:
    command: str        # Command executed
    success: bool       # True if exit code 0
    output: str         # Standard output
    error: str          # Error output
    exit_code: int      # Command exit code
```

## Changelog

### v3.0 - Sudo Capabilities

- ✅ Added `SudoExecutor` with pexpect
- ✅ Integrated into CLI agent
- ✅ Integrated into Desktop app
- ✅ Safety validation (NEVER_ALLOW, HIGH_RISK)
- ✅ Password caching
- ✅ User confirmation prompts
- ✅ Comprehensive documentation

### Previous Versions

- v2.0: Desktop app with system tray
- v1.0: CLI agent with safe command execution

## Support

For issues, questions, or suggestions:
1. Check troubleshooting section above
2. Review command logs: `sudo grep sudo /var/log/auth.log`
3. Test sudo executor directly: `python3 tools/execution/sudo_executor.py sudo true`
4. Report bugs with full error messages and command used

---

**Remember**: With great power comes great responsibility. Sudo capabilities are powerful—use them wisely! 🔐
