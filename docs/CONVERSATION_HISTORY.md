# Conversation History Feature

The Llama GPU Assistant now automatically saves and restores your conversation history across sessions!

---

## Overview

Your conversations with the AI assistant are now **persistent**. When you close the app and reopen it, your previous conversations are automatically restored, allowing you to continue where you left off.

### Key Features

- ✅ **Automatic Save**: History is saved when you quit the application
- ✅ **Automatic Load**: Previous conversations are restored on startup
- ✅ **Manual Save**: Save history anytime from the menu
- ✅ **Clear History**: Delete all saved conversations with confirmation
- ✅ **Size Management**: Automatically limits history to prevent unbounded growth
- ✅ **Backup Creation**: Creates backups before clearing or when file is corrupted
- ✅ **Safe Storage**: Uses atomic writes to prevent data corruption

---

## How It Works

### Automatic Save on Exit

When you quit the application (via menu or window close):
1. All conversation messages are collected
2. Timestamps are added to each message
3. Data is saved to a JSON file
4. Application exits cleanly

### Automatic Load on Startup

When you launch the application:
1. History file is checked for existence
2. Previous conversations are loaded from disk
3. Chat window displays: "═══ Previous Conversation ═══"
4. All previous messages are restored
5. A separator shows: "═══ Current Session ═══"
6. You can continue the conversation seamlessly

---

## Storage Location

History is stored using XDG standards:

```
~/.local/share/llama-gpu-assistant/
└── conversation_history.json
```

### File Format

```json
{
  "version": "1.0",
  "saved_at": "2025-11-12T14:30:00.123456",
  "conversations": [
    {
      "role": "user",
      "content": "Hello, how are you?",
      "timestamp": 1731427800.123
    },
    {
      "role": "assistant",
      "content": "I'm doing great! How can I help you?",
      "timestamp": 1731427801.456
    }
  ]
}
```

---

## Using the History Features

### View Previous Conversations

1. Launch the app
2. Click the system tray icon to open chat
3. Scroll up to see previous conversations
4. Look for the "═══ Previous Conversation ═══" separator

### Manual Save

To save your current conversation manually:

**From Tray Menu:**
1. Right-click the system tray icon
2. Select "💾 Save History"
3. Notification confirms save

### Clear History

To delete all saved conversations:

**From Tray Menu:**
1. Right-click the system tray icon
2. Select "🗑️ Clear History"
3. Confirm the action
4. A backup is created before clearing

**Note**: Clearing history is permanent (though a backup is kept).

---

## Configuration

### History Limits

The system automatically manages history size:

- **Max Items**: 1,000 conversation messages
- **Max File Size**: 10 MB
- **Behavior**: Keeps only the most recent messages

### When Limits Are Reached

If the history file exceeds limits:
1. A backup is created with timestamp
2. Old messages are truncated
3. Only recent messages are kept

---

## Troubleshooting

### History Not Loading

**Symptom**: Previous conversations don't appear on startup

**Solutions**:

1. **Check History File**:
   ```bash
   ls -lh ~/.local/share/llama-gpu-assistant/conversation_history.json
   ```

2. **Check for Backups**:
   ```bash
   ls -lh ~/.local/share/llama-gpu-assistant/
   ```

3. **Check Permissions**:
   ```bash
   chmod 644 ~/.local/share/llama-gpu-assistant/conversation_history.json
   ```

4. **View Logs**:
   Launch app from terminal to see loading messages:
   ```bash
   ./bin/llama-assistant
   ```

### Corrupted History File

**Symptom**: Error messages about JSON decoding

**What Happens**:
- Corrupted file is automatically renamed with `.corrupted` suffix
- New clean history file is created
- App continues to work normally

**Recovery**:
```bash
cd ~/.local/share/llama-gpu-assistant/
ls -lt  # Find the corrupted file
cat conversation_history.corrupted.*.json  # Try to recover data manually
```

### History File Too Large

**Symptom**: File exceeds 10MB limit

**What Happens**:
- File is automatically renamed with `.backup` suffix
- New clean history file is created
- Only recent conversations are kept

**Adjust Limits** (if needed):
Edit `tools/gui/ai_assistant_app.py`:
```python
class ConversationHistory:
    def __init__(self, history_dir=None):
        self.max_history_items = 2000  # Increase from 1000
        self.max_file_size = 20 * 1024 * 1024  # 20MB instead of 10MB
```

---

## Advanced Usage

### Export History

To export your conversation history:

```python
from tools.gui.ai_assistant_app import ConversationHistory

history = ConversationHistory()
history.export_history('/path/to/export.json')
```

### Import History

To import from a backup:

```bash
cp backup_file.json ~/.local/share/llama-gpu-assistant/conversation_history.json
```

### Programmatic Access

Access history programmatically:

```python
from tools.gui.ai_assistant_app import ConversationHistory
import json

# Load history
history_manager = ConversationHistory()
conversations = history_manager.load_history()

# Display
for conv in conversations:
    role = conv['role']
    content = conv['content']
    timestamp = conv.get('timestamp', 0)
    print(f"[{timestamp}] {role}: {content[:50]}...")

# Modify and save
# ... make changes ...
history_manager.save_history(conversations)
```

---

## Privacy & Security

### What Is Stored

- All conversation messages (user and AI responses)
- Message timestamps
- Message roles (user, assistant, system)
- Command execution results (if displayed in chat)

### What Is NOT Stored

- Passwords (from sudo prompts)
- API keys or credentials
- System information (unless explicitly asked for in chat)

### Data Location

All history is stored **locally** on your machine:
- Not sent to any cloud service
- Not shared with any third party
- Stored in your personal user directory

### Deleting History

To permanently delete all history:

**Method 1: Via App**
1. Right-click tray icon → "🗑️ Clear History"

**Method 2: Manual Deletion**
```bash
rm -rf ~/.local/share/llama-gpu-assistant/
```

**Method 3: Secure Deletion**
```bash
shred -vfz ~/.local/share/llama-gpu-assistant/conversation_history.json
rm -rf ~/.local/share/llama-gpu-assistant/
```

---

## Data Recovery

### Backups Are Created

Automatic backups are created:
- When clearing history: `conversation_history.cleared.TIMESTAMP.json`
- When file is corrupted: `conversation_history.corrupted.TIMESTAMP.json`
- When file is too large: `conversation_history.backup.TIMESTAMP.json`

### Restoring from Backup

```bash
cd ~/.local/share/llama-gpu-assistant/

# List available backups
ls -lh conversation_history.*.json

# Restore a backup
cp conversation_history.backup.1731427800.json conversation_history.json

# Restart the app
./bin/llama-assistant
```

---

## Technical Details

### Implementation

The history system uses:
- **JSON Format**: Human-readable and editable
- **Atomic Writes**: Writes to temp file, then replaces (prevents corruption)
- **Size Limits**: Prevents unbounded growth
- **Timestamps**: Unix timestamps for precise timing
- **XDG Standards**: Follows Linux desktop standards

### Code Structure

```python
ConversationHistory          # Manages persistence
├── load_history()          # Load from disk
├── save_history()          # Save to disk
├── clear_history()         # Delete with backup
└── export_history()        # Export to file

ChatWindow                   # GUI window
├── _load_conversation_history()   # On startup
├── _display_loaded_history()      # Show in UI
└── save_conversation_history()    # On shutdown
```

### Thread Safety

The implementation is thread-safe:
- File operations use atomic writes
- GTK updates use `GLib.idle_add()`
- No race conditions in save/load

---

## Testing

Test the history functionality:

```bash
# Run test script
python3 test_history.py

# Expected output:
# ✅ Saved 4 conversations
# ✅ Loaded 4 conversations
# ✅ All tests passed!
```

---

## Future Enhancements

Potential improvements:
- [ ] Search through history
- [ ] Filter by date range
- [ ] Export to different formats (Markdown, PDF)
- [ ] Conversation tags/categories
- [ ] History encryption
- [ ] Cloud sync (optional)
- [ ] Multiple history profiles

---

## See Also

- [Desktop App Installation](DESKTOP_APP_INSTALLATION.md)
- [Main README](../README.md)
- [GUI Setup Guide](GUI-SETUP-COMPLETE.md)

---

**Version**: 1.0.0
**Last Updated**: November 12, 2025
**Status**: Production Ready ✅
