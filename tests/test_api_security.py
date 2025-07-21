import pytest
from src.api_security import authenticate_request, log_api_event

def test_authenticate_request_logs():
    assert authenticate_request('test_request')
    with open('logs/api_security.log') as log:
        assert 'Authentication called' in log.read()

def test_log_api_event_logs():
    log_api_event('test_event')
    with open('logs/api_security.log') as log:
        assert 'API event: test_event' in log.read()
