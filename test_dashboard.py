#!/usr/bin/env python3
print('Testing Flask dashboard import...')
try:
    from src.dashboard import app, socketio
    print('✅ Flask dashboard imports successfully')
    print('📍 Ready to start on http://localhost:5000')
except Exception as e:
    print(f'❌ Error: {e}')
