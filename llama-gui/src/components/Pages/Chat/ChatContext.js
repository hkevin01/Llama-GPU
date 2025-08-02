import { createContext, useContext, useEffect, useReducer } from 'react';

// Initial state
const initialState = {
  messages: [],
  isConnected: false,
  isTyping: false,
  metrics: {
    tokensPerSec: 0,
    gpuUsage: 0,
    responseTime: 0,
  },
  gpuStatus: {
    available: false,
    name: '',
    memoryUsed: 0,
    memoryTotal: 0,
  },
  currentStream: {
    content: '',
    startTime: null,
    tokenCount: 0,
  },
};

// Action types
export const ACTIONS = {
  SET_CONNECTED: 'SET_CONNECTED',
  ADD_MESSAGE: 'ADD_MESSAGE',
  UPDATE_STREAM: 'UPDATE_STREAM',
  END_STREAM: 'END_STREAM',
  SET_TYPING: 'SET_TYPING',
  UPDATE_METRICS: 'UPDATE_METRICS',
  UPDATE_GPU_STATUS: 'UPDATE_GPU_STATUS',
  RESET_STREAM: 'RESET_STREAM',
};

// Reducer function
function chatReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_CONNECTED:
      return { ...state, isConnected: action.payload };

    case ACTIONS.ADD_MESSAGE:
      return {
        ...state,
        messages: [...state.messages, action.payload],
      };

    case ACTIONS.UPDATE_STREAM:
      return {
        ...state,
        currentStream: {
          ...state.currentStream,
          content: state.currentStream.content + action.payload,
          tokenCount: state.currentStream.tokenCount + 1,
        },
      };

    case ACTIONS.END_STREAM:
      return {
        ...state,
        messages: [
          ...state.messages,
          {
            role: 'assistant',
            content: state.currentStream.content,
            timestamp: new Date().toISOString(),
          },
        ],
        currentStream: {
          content: '',
          startTime: null,
          tokenCount: 0,
        },
      };

    case ACTIONS.SET_TYPING:
      return { ...state, isTyping: action.payload };

    case ACTIONS.UPDATE_METRICS:
      return {
        ...state,
        metrics: { ...state.metrics, ...action.payload },
      };

    case ACTIONS.UPDATE_GPU_STATUS:
      return {
        ...state,
        gpuStatus: { ...state.gpuStatus, ...action.payload },
      };

    case ACTIONS.RESET_STREAM:
      return {
        ...state,
        currentStream: {
          content: '',
          startTime: Date.now(),
          tokenCount: 0,
        },
      };

    default:
      return state;
  }
}

// Create context
const ChatContext = createContext();

// Context provider component
export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Setup WebSocket connection
  useEffect(() => {
    let ws = null;
    let reconnectTimer = null;

    const connect = () => {
      try {
        ws = new WebSocket('ws://localhost:8000/v1/stream');

        ws.onopen = () => {
          dispatch({ type: ACTIONS.SET_CONNECTED, payload: true });
          console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        };

        ws.onclose = () => {
          dispatch({ type: ACTIONS.SET_CONNECTED, payload: false });
          console.log('WebSocket disconnected');
          // Attempt to reconnect after 3 seconds
          reconnectTimer = setTimeout(connect, 3000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          ws.close();
        };
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        reconnectTimer = setTimeout(connect, 3000);
      }
    };

    const handleWebSocketMessage = (data) => {
      switch (data.type) {
        case 'token':
          dispatch({ type: ACTIONS.UPDATE_STREAM, payload: data.content });
          break;
        case 'metrics':
          dispatch({ type: ACTIONS.UPDATE_METRICS, payload: data.metrics });
          break;
        case 'complete':
          dispatch({ type: ACTIONS.END_STREAM });
          break;
        case 'error':
          console.error('Server error:', data.error);
          dispatch({
            type: ACTIONS.ADD_MESSAGE,
            payload: {
              role: 'assistant',
              content: 'Sorry, I encountered an error. Please try again.',
              timestamp: new Date().toISOString(),
            },
          });
          break;
        default:
          break;
      }
    };

    // Initialize connection
    connect();

    // Setup GPU status polling
    const pollGPUStatus = async () => {
      try {
        const response = await fetch('/v1/monitor/gpu-status');
        const data = await response.json();
        dispatch({ type: ACTIONS.UPDATE_GPU_STATUS, payload: data });
      } catch (error) {
        console.error('Failed to fetch GPU status:', error);
      }
    };

    const gpuPollInterval = setInterval(pollGPUStatus, 5000);
    pollGPUStatus(); // Initial poll

    // Cleanup
    return () => {
      if (ws) {
        ws.close();
      }
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      clearInterval(gpuPollInterval);
    };
  }, []);

  return (
    <ChatContext.Provider value={{ state, dispatch }}>
      {children}
    </ChatContext.Provider>
  );
}

// Custom hook for using chat context
export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
}
