import { keyframes } from '@emotion/react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import { styled, Theme } from '@mui/material/styles';
import React from 'react';

// Extend Material-UI's default props and style overrides
declare module '@mui/material/styles' {
  interface Components {
    MuiStatusIndicator: {
      defaultProps?: {
        connected?: boolean;
      };
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
    MuiGPUStatus: {
      defaultProps?: {
        status?: 'available' | 'unavailable';
      };
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
    MuiMessageContainer: {
      defaultProps?: {
        role?: 'user' | 'assistant';
      };
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
    MuiMessageContent: {
      defaultProps?: {
        role?: 'user' | 'assistant';
      };
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
    MuiTypingDot: {
      defaultProps?: {
        index?: number;
      };
      styleOverrides?: {
        root?: React.CSSProperties;
      };
    };
  }
}

// Animations
const blink = keyframes`
  0% { opacity: 0.3; }
  20% { opacity: 1; }
  100% { opacity: 0.3; }
`;

// Container for the entire chat interface
export const ChatContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  backgroundColor: theme.palette.background.default,
}));

// Chat header component
export const ChatHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[1],
  zIndex: 1,
  gap: theme.spacing(2),
}));

// Status indicator for connection state
interface StatusIndicatorProps {
  connected: boolean;
  theme?: Theme;
}

const StatusIndicatorRoot = styled('div', {
  shouldForwardProp: (prop) => prop !== 'connected',
})<StatusIndicatorProps>(
  ({ theme, connected }) => ({
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    backgroundColor: connected ? theme.palette.success.main : theme.palette.error.main,
    transition: 'background-color 0.3s ease',
  })
);

export const StatusIndicator = React.forwardRef<HTMLDivElement, StatusIndicatorProps>(
  (props, ref) => <StatusIndicatorRoot {...props} ref={ref} />
);

// Performance metrics container
export const PerformanceMetrics = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(2),
  marginLeft: 'auto',
}));

// Individual metric container
export const Metric = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
}));

// GPU status display
interface GPUStatusProps {
  status: 'available' | 'unavailable';
}

export const GPUStatus = styled(Paper)<GPUStatusProps>(
  ({ theme, status }) => ({
    margin: theme.spacing(2),
    padding: theme.spacing(1, 2),
    backgroundColor: status === 'available'
      ? theme.palette.success.light
      : theme.palette.warning.light,
    color: theme.palette.text.primary,
    display: 'inline-flex',
    alignItems: 'center',
    alignSelf: 'flex-start',
  })
);

// Chat messages container
export const ChatMessages = styled('div')`
  flex: 1;
  overflow-y: auto;
  padding: ${({ theme }) => theme.spacing(2)};
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing(2)};
`;

// Individual message container
interface MessageProps {
  role: 'user' | 'assistant';
}

export const MessageContainer = styled(Box)<MessageProps>(
  ({ theme, role }) => ({
    display: 'flex',
    justifyContent: role === 'user' ? 'flex-end' : 'flex-start',
    marginBottom: theme.spacing(1),
  })
);

// Message content component
export const MessageContent = styled(Paper)<MessageProps>(
  ({ theme, role }) => ({
    padding: theme.spacing(1, 2),
    maxWidth: '80%',
    backgroundColor: role === 'user' ? theme.palette.primary.light : theme.palette.grey[100],
    color: role === 'user' ? theme.palette.primary.contrastText : theme.palette.text.primary,
  })
);

// Typing indicator component
export const TypingIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  padding: theme.spacing(1),
}));

export const TypingDots = styled(Box)({
  display: 'flex',
  gap: '4px',
});

// Individual typing dot
interface TypingDotProps {
  index: number;
}

export const TypingDot = styled(Box)<TypingDotProps>(
  ({ theme, index }) => ({
    width: '8px',
    height: '8px',
    backgroundColor: theme.palette.grey[400],
    borderRadius: '50%',
    animation: `${blink} 1.4s infinite`,
    animationDelay: `${index * 0.2}s`,
  })
);

// Chat input container
export const ChatInputContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[1],
}));
