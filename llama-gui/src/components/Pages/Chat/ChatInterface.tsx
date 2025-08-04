import React, { useEffect, useRef, useState } from 'react';

// Material UI imports
import SendIcon from '@mui/icons-material/Send';
import StopIcon from '@mui/icons-material/Stop';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

// Local imports
import { getCurrentConfig } from '../../../config/llm-config';
import { ACTIONS, useChatContext } from './ChatContext';
import {
    ChatContainer,
    ChatHeader,
    ChatInputContainer,
    ChatMessages,
    GPUStatus,
    MessageContainer,
    MessageContent,
    Metric,
    PerformanceMetrics,
    StatusIndicator,
    TypingDot,
    TypingDots,
    TypingIndicator,
} from './ChatStyles';
import type { Message } from './types';

// Type guard for Message type
function isMessage(message: any): message is Message {
  return (
    typeof message === 'object' &&
    message !== null &&
    'role' in message &&
    'content' in message &&
    'timestamp' in message
  );
}

function ChatInterface() {
  const { state, dispatch } = useChatContext();
  const [input, setInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);

  // Setup WebSocket connection
  const setupWebSocket = React.useCallback(() => {
    const config = getCurrentConfig();
    const wsUrl = `ws://${config.baseUrl.replace('http://', '')}${config.wsEndpoint}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      dispatch({ type: ACTIONS.SET_CONNECTION, payload: true });
      console.log('WebSocket connected');
    };

    ws.onclose = () => {
      dispatch({ type: ACTIONS.SET_CONNECTION, payload: false });
      console.log('WebSocket disconnected');
      if (reconnectTimerRef.current) {
        window.clearTimeout(reconnectTimerRef.current);
      }
      reconnectTimerRef.current = window.setTimeout(() => {
        wsRef.current = setupWebSocket();
      }, 5000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received WebSocket message:', data);

        switch (data.type) {
          case 'message':
            if (isMessage(data)) {
              const message: Message = {
                role: data.role,
                content: data.content,
                timestamp: data.timestamp
              };
              dispatch({ type: ACTIONS.ADD_MESSAGE, payload: message });
            }
            break;

          case 'start':
            console.log('Starting new message stream');
            dispatch({ type: ACTIONS.SET_TYPING, payload: true });
            break;

          case 'token':
            if (typeof data.content !== 'string') {
              console.warn('Invalid token content:', data.content);
              break;
            }
            dispatch({ type: ACTIONS.UPDATE_STREAM, payload: data.content });
            break;

          case 'metrics':
            if (typeof data.metrics !== 'object') {
              console.warn('Invalid metrics data:', data.metrics);
              break;
            }
            dispatch({ type: ACTIONS.UPDATE_METRICS, payload: data.metrics });
            break;

          case 'end':
            console.log('Ending message stream');
            dispatch({ type: ACTIONS.END_STREAM });
            dispatch({ type: ACTIONS.SET_TYPING, payload: false });
            break;

          case 'error':
            console.error('Server error:', data.message);
            setError(data.message || 'Unknown server error');
            dispatch({ type: ACTIONS.SET_TYPING, payload: false });
            break;

          default:
            console.warn('Unknown message type:', data.type);
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
        setError('Failed to process server response');
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error. Retrying...');
    };

    return ws;
  }, [dispatch, setError]);

  // Handle message submission
  const handleSubmit = React.useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    const message = input.trim();
    if (!message) return;

    // Create and add user message
    const userMessage: Message = {
      role: 'user' as const,
      content: message,
      timestamp: new Date().toISOString(),
    };
    dispatch({
      type: ACTIONS.ADD_MESSAGE,
      payload: userMessage,
    });

    // Reset input and prepare for stream
    setInput('');
    dispatch({ type: ACTIONS.RESET_STREAM });
    dispatch({ type: ACTIONS.SET_TYPING, payload: true });

    if (!state.isConnected) {
      setError('Not connected to server');
      return;
    }

    try {
      // Send the message through WebSocket
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        throw new Error('WebSocket is not connected');
      }

      try {
        wsRef.current.send(JSON.stringify({
          type: 'message',
          content: message,
          timestamp: new Date().toISOString()
        }));
      } catch (err) {
        if (err instanceof Error) {
          throw new Error(`Failed to send message through WebSocket: ${err.message}`);
        }
        throw new Error('Failed to send message through WebSocket');
      }
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Unknown error occurred');
      }
    }
  }, [input, state.isConnected, dispatch, setInput, setError]);

  // Initialize WebSocket connection
  useEffect(() => {
    wsRef.current = setupWebSocket();

    return () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
      if (reconnectTimerRef.current) {
        window.clearTimeout(reconnectTimerRef.current);
      }
    };
  }, [setupWebSocket]);

  // Scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.messages, state.currentStream.content]);

  // Reset error when input changes
  useEffect(() => {
    if (error) {
      setError(null);
    }
  }, [input, error]);

  return (
    <ChatContainer>
      <ChatHeader>
        <Typography variant="h6">🦙 Llama-GPU Chat</Typography>
        <StatusIndicator connected={state.isConnected} />
        <PerformanceMetrics>
          <Metric>
            <Typography variant="caption">Speed</Typography>
            <Typography variant="body2">
              {((state.metrics as any).tokensPerSecond || 0).toFixed(1)} tok/s
            </Typography>
          </Metric>
          <Metric>
            <Typography variant="caption">GPU Usage</Typography>
            <Typography variant="body2">
              {state.metrics.gpuUsage}%
            </Typography>
          </Metric>
          <Metric>
            <Typography variant="caption">Response Time</Typography>
            <Typography variant="body2">
              {state.metrics.responseTime} ms
            </Typography>
          </Metric>
        </PerformanceMetrics>
      </ChatHeader>

      <GPUStatus
        status={state.gpuStatus.available ? 'available' : 'unavailable'}
        elevation={3}
      >
        {state.gpuStatus.available ? (
          `GPU: ${state.gpuStatus.name} (${state.gpuStatus.memoryUsed}/${state.gpuStatus.memoryTotal}GB)`
        ) : (
          'GPU: CPU Only'
        )}
      </GPUStatus>

      <ChatMessages>
        {(state.messages as Message[]).map((message, index) => (
          <MessageContainer
            key={message.timestamp || index}
            role={message.role}
          >
            <MessageContent role={message.role} elevation={1}>
              <Typography>{message.content}</Typography>
            </MessageContent>
          </MessageContainer>
        ))}

        {state.currentStream.content && (
          <MessageContainer role="assistant">
            <MessageContent role="assistant" elevation={1}>
              <Typography>{state.currentStream.content}</Typography>
            </MessageContent>
          </MessageContainer>
        )}

        {state.isTyping && (
          <TypingIndicator>
            <TypingDots>
              {[0, 1, 2].map((i) => (
                <TypingDot key={i} index={i} />
              ))}
            </TypingDots>
          </TypingIndicator>
        )}

        <div ref={messagesEndRef} />
      </ChatMessages>

      <ChatInputContainer>
        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{
            display: 'flex',
            gap: 1,
            alignItems: 'center',
          }}
        >
          <TextField
            fullWidth
            placeholder="Type your message here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            multiline
            maxRows={4}
            disabled={state.isTyping}
            error={!!error}
            helperText={error || ''}
            inputRef={inputRef}
          />
          <IconButton
            color="primary"
            type="submit"
            disabled={!input.trim() || state.isTyping}
          >
            <SendIcon />
          </IconButton>
          {state.isTyping && (
            <IconButton
              color="error"
              onClick={() => {
                if (wsRef.current?.readyState === WebSocket.OPEN) {
                  wsRef.current.send(JSON.stringify({ type: 'stop' }));
                }
              }}
            >
              <StopIcon />
            </IconButton>
          )}
        </Box>
      </ChatInputContainer>
    </ChatContainer>
  );
}

export default ChatInterface;
