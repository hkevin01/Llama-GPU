import {
    Send as SendIcon,
    Stop as StopIcon,
} from '@mui/icons-material';
import {
    Box,
    IconButton,
    TextField,
    Typography,
} from '@mui/material';
import { useEffect, useRef, useState } from 'react';
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

function ChatInterface() {
  const { state, dispatch } = useChatContext();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom when messages update
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.messages, state.currentStream.content]);

  // Calculate real-time metrics
  const calculateMetrics = () => {
    if (state.currentStream.startTime) {
      const elapsed = (Date.now() - state.currentStream.startTime) / 1000;
      return elapsed > 0
        ? (state.currentStream.tokenCount / elapsed).toFixed(1)
        : '0';
    }
    return '0';
  };

  // Process each line from the server response
  const processLine = (line, dispatch) => {
    if (!line.startsWith('data: ')) return;

    const data = line.slice(6);
    if (data === '[DONE]') {
      dispatch({ type: ACTIONS.END_STREAM });
      dispatch({ type: ACTIONS.SET_TYPING, payload: false });
      return true;
    }

    try {
      const parsed = JSON.parse(data);
      if (parsed.choices?.[0]?.delta?.content) {
        dispatch({
          type: ACTIONS.UPDATE_STREAM,
          payload: parsed.choices[0].delta.content,
        });
      }
    } catch (e) {
      console.warn('Failed to parse stream chunk:', e);
    }
    return false;
  };

  // Process response from server
  const processResponse = async (response, dispatch) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let isDone = false;

    while (!isDone) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (processLine(line, dispatch)) {
          isDone = true;
          break;
        }
      }
    }
  };

  // Make HTTP request to chat endpoint
  const makeHttpRequest = async (message) => {
    const response = await fetch('/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama-base',
        messages: [{ role: 'user', content: message }],
        stream: true,
        max_tokens: 500,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  };

  // Handle error during chat request
  const handleError = (dispatch, error) => {
    console.error('Chat request failed:', error);
    dispatch({
      type: ACTIONS.ADD_MESSAGE,
      payload: {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      },
    });
    dispatch({ type: ACTIONS.SET_TYPING, payload: false });
  };

  // Handle message submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    const message = input.trim();
    if (!message) return;

    // Add user message
    dispatch({
      type: ACTIONS.ADD_MESSAGE,
      payload: {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      },
    });

    // Reset input and prepare for stream
    setInput('');
    dispatch({ type: ACTIONS.RESET_STREAM });
    dispatch({ type: ACTIONS.SET_TYPING, payload: true });

    if (!state.isConnected) {
      try {
        const response = await makeHttpRequest(message);
        await processResponse(response, dispatch);
      } catch (error) {
        handleError(dispatch, error);
      }
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <Typography variant="h6">🦙 Llama-GPU Chat</Typography>
        <StatusIndicator connected={state.isConnected} />
        <PerformanceMetrics>
          <Metric>
            <Typography variant="caption">Speed</Typography>
            <Typography variant="body2">
              {calculateMetrics()} tok/s
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
        {state.messages.map((message, index) => (
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
            ref={inputRef}
            disabled={state.isTyping}
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
                // Implement stop generation
                console.log('Stop generation');
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
