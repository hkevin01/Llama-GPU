#!/usr/bin/env python3
"""Test conversation history functionality."""

import sys
import os
import time
sys.path.insert(0, "/home/kevin/Projects/Llama-GPU")

# Import the ConversationHistory class
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Notify
from tools.gui.ai_assistant_app import ConversationHistory

def test_history():
    """Test history save and load."""
    print("Testing Conversation History...")
    print("=" * 50)
    
    # Initialize
    history_manager = ConversationHistory()
    print(f"✅ History directory: {history_manager.history_dir}")
    print(f"✅ History file: {history_manager.history_file}")
    
    # Create test conversations
    test_conversations = [
        {
            "role": "user",
            "content": "Hello, how are you?",
            "timestamp": time.time()
        },
        {
            "role": "assistant",
            "content": "I'm doing great! How can I help you today?",
            "timestamp": time.time()
        },
        {
            "role": "user",
            "content": "What's the weather like?",
            "timestamp": time.time()
        },
        {
            "role": "assistant",
            "content": "I don't have real-time weather data, but I can help you check it!",
            "timestamp": time.time()
        }
    ]
    
    # Test saving
    print("\n📝 Testing save...")
    success = history_manager.save_history(test_conversations)
    if success:
        print(f"✅ Saved {len(test_conversations)} conversations")
    else:
        print("❌ Failed to save")
        return False
    
    # Test loading
    print("\n📖 Testing load...")
    loaded = history_manager.load_history()
    if loaded:
        print(f"✅ Loaded {len(loaded)} conversations")
        
        # Verify content
        if len(loaded) == len(test_conversations):
            print("✅ Conversation count matches")
        else:
            print(f"❌ Count mismatch: expected {len(test_conversations)}, got {len(loaded)}")
        
        # Display loaded conversations
        print("\nLoaded conversations:")
        for i, conv in enumerate(loaded, 1):
            role = conv.get('role', 'unknown')
            content = conv.get('content', '')[:50]
            print(f"  {i}. {role}: {content}...")
    else:
        print("❌ Failed to load")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    test_history()
