import { Box, Paper } from '@mui/material';
import { styled } from '@mui/material/styles';
import { keyframes } from '@mui/system';

// Keyframe animations
const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const typing = keyframes`
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
`;

const pulse = keyframes`
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
`;

// Styled components
export const ChatContainer = styled(Paper)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 128px)', // Account for header and padding
  backgroundColor: theme.palette.background.paper,
  overflow: 'hidden',
  borderRadius: theme.shape.borderRadius * 1.5,
  boxShadow: theme.shadows[3],
}));

export const ChatHeader = styled(Box)(({ theme }) => ({
  background: theme.palette.mode === 'dark'
    ? `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.secondary.dark})`
    : `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  color: theme.palette.common.white,
  padding: theme.spacing(2),
  textAlign: 'center',
  position: 'relative',
}));

export const StatusIndicator = styled('div')(({ theme, connected }) => ({
  position: 'absolute',
  top: theme.spacing(2),
  right: theme.spacing(2),
  width: 12,
  height: 12,
  backgroundColor: connected ? theme.palette.success.main : theme.palette.error.main,
  borderRadius: '50%',
  animation: `${pulse} 2s infinite`,
}));

export const PerformanceMetrics = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-around',
  fontSize: '0.8em',
  marginTop: theme.spacing(1),
}));

export const Metric = styled(Box)({
  textAlign: 'center',
});

export const ChatMessages = styled(Box)(({ theme }) => ({
  flex: 1,
  overflowY: 'auto',
  padding: theme.spacing(2),
  backgroundColor: theme.palette.mode === 'dark'
    ? theme.palette.background.default
    : theme.palette.grey[50],
}));

export const MessageContainer = styled(Box)(({ theme, role }) => ({
  marginBottom: theme.spacing(2),
  display: 'flex',
  justifyContent: role === 'user' ? 'flex-end' : 'flex-start',
  animation: `${fadeIn} 0.3s ease-in`,
}));

export const MessageContent = styled(Paper)(({ theme, role }) => ({
  maxWidth: '70%',
  padding: theme.spacing(1.5, 2),
  borderRadius: theme.spacing(2),
  wordWrap: 'break-word',
  ...(role === 'user' ? {
    background: theme.palette.mode === 'dark'
      ? `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.secondary.dark})`
      : `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
    color: theme.palette.common.white,
  } : {
    backgroundColor: theme.palette.background.paper,
    color: theme.palette.text.primary,
    border: `1px solid ${theme.palette.divider}`,
  }),
}));

export const TypingIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  padding: theme.spacing(1.5, 2),
  background: theme.palette.background.paper,
  borderRadius: theme.spacing(2),
  marginBottom: theme.spacing(2),
  border: `1px solid ${theme.palette.divider}`,
}));

export const TypingDots = styled(Box)({
  display: 'flex',
  gap: '4px',
});

export const TypingDot = styled('div')(({ theme, index }) => ({
  width: 8,
  height: 8,
  backgroundColor: theme.palette.grey[400],
  borderRadius: '50%',
  animation: `${typing} 1.4s infinite`,
  animationDelay: `${index * 0.2}s`,
}));

export const ChatInputContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderTop: `1px solid ${theme.palette.divider}`,
}));

export const GPUStatus = styled(Paper)(({ theme, status }) => ({
  position: 'absolute',
  top: theme.spacing(2),
  right: theme.spacing(2),
  padding: theme.spacing(1, 2),
  borderRadius: theme.spacing(1),
  fontSize: '0.8em',
  zIndex: 1000,
  backgroundColor: status === 'available'
    ? theme.palette.success.dark
    : status === 'unavailable'
      ? theme.palette.warning.dark
      : theme.palette.error.dark,
  color: theme.palette.common.white,
}));
