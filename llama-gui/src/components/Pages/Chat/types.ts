import { Theme } from '@mui/material/styles';
import React from 'react';

// Chat Message Types
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

// GPU Status Types
export interface GPUStatusType {
  available: boolean;
  name: string;
  memoryUsed: number;
  memoryTotal: number;
}

// Chat State Types
export interface ChatState {
  messages: Message[];
  currentStream: {
    content: string;
    startTime: number;
    tokenCount: number;
  };
  isConnected: boolean;
  isTyping: boolean;
  metrics: {
    gpuUsage: number;
    responseTime: number;
  };
  gpuStatus: GPUStatusType;
}

// Action Types
export type CustomDispatch = (action: {
  type: string;
  payload?: any;
}) => void;

// UI Component Props
export interface StatusIndicatorProps {
  connected: boolean;
  theme?: Theme;
}

export interface GPUStatusProps {
  status: 'available' | 'unavailable';
  elevation: number;
  children: React.ReactNode;
}

export interface MessageProps {
  role: 'user' | 'assistant';
}

export interface TypingDotProps {
  index: number;
}

declare module '@mui/material/styles' {
  interface Components {
    StatusIndicator: {
      defaultProps?: Partial<StatusIndicatorProps>;
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
    GPUStatus: {
      defaultProps?: Partial<GPUStatusProps>;
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
    TypingDot: {
      defaultProps?: Partial<TypingDotProps>;
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
  }
}
