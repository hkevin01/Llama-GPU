import React, { createContext, ReactNode, useContext, useReducer } from 'react';
import { ChatState } from './chat-types';

interface Action {
  type: string;
  payload?: any;
}

export const ACTIONS = {
  ADD_MESSAGE: 'ADD_MESSAGE',
  UPDATE_STREAM: 'UPDATE_STREAM',
  RESET_STREAM: 'RESET_STREAM',
  END_STREAM: 'END_STREAM',
  SET_TYPING: 'SET_TYPING',
  UPDATE_METRICS: 'UPDATE_METRICS',
  UPDATE_GPU_STATUS: 'UPDATE_GPU_STATUS',
  SET_CONNECTION: 'SET_CONNECTION',
} as const;

const initialState: ChatState = {
  messages: [],
  currentStream: {
    content: '',
    startTime: 0,
    tokenCount: 0,
  },
  isConnected: false,
  isTyping: false,
  metrics: {
    gpuUsage: 0,
    responseTime: 0,
  },
  gpuStatus: {
    available: false,
    name: '',
    memoryUsed: 0,
    memoryTotal: 0,
  },
};

const reducer = (state: ChatState, action: Action): ChatState => {
  switch (action.type) {
    case ACTIONS.ADD_MESSAGE:
      return {
        ...state,
        messages: [...state.messages, action.payload],
      };

    case ACTIONS.UPDATE_STREAM: {
      const now = Date.now();
      return {
        ...state,
        currentStream: {
          content: state.currentStream.content + action.payload,
          startTime: state.currentStream.startTime || now,
          tokenCount: state.currentStream.tokenCount + 1,
        },
      };
    }

    case ACTIONS.RESET_STREAM:
      return {
        ...state,
        currentStream: {
          content: '',
          startTime: 0,
          tokenCount: 0,
        },
      };

    case ACTIONS.END_STREAM:
      if (state.currentStream.content) {
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
            startTime: 0,
            tokenCount: 0,
          },
        };
      }
      return state;

    case ACTIONS.SET_TYPING:
      return {
        ...state,
        isTyping: action.payload,
      };

    case ACTIONS.UPDATE_METRICS:
      return {
        ...state,
        metrics: {
          ...state.metrics,
          ...action.payload,
        },
      };

    case ACTIONS.UPDATE_GPU_STATUS:
      return {
        ...state,
        gpuStatus: {
          ...state.gpuStatus,
          ...action.payload,
        },
      };

    case ACTIONS.SET_CONNECTION:
      return {
        ...state,
        isConnected: action.payload,
      };

    default:
      return state;
  }
};

const ChatContext = createContext<{
  state: ChatState;
  dispatch: React.Dispatch<Action>;
} | null>(null);

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider = ({ children }: ChatProviderProps) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const value = React.useMemo(() => ({ state, dispatch }), [state]);

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
};
