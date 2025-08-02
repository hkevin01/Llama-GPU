import { Theme } from '@mui/material/styles';
import React from 'react';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface GPUStatusType {
  available: boolean;
  name: string;
  memoryUsed: number;
  memoryTotal: number;
}

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

export type CustomDispatch = (action: {
  type: string;
  payload?: any;
}) => void;

declare module '@mui/material/styles' {
  interface Components {
    StatusIndicator: {
      defaultProps?: Partial<import('./types').StatusIndicatorProps>;
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
    GPUStatus: {
      defaultProps?: Partial<import('./types').GPUStatusProps>;
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
    TypingDot: {
      defaultProps?: Partial<import('./types').TypingDotProps>;
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
  }
}
