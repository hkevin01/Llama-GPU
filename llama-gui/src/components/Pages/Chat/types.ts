import { Theme } from '@mui/material/styles';

export interface StyledComponentProps {
  theme?: Theme;
}

export interface StatusIndicatorProps extends StyledComponentProps {
  connected: boolean;
}

export interface GPUStatusProps extends StyledComponentProps {
  status: 'available' | 'unavailable';
  elevation?: number;
}

export interface MessageProps extends StyledComponentProps {
  role: 'user' | 'assistant';
}

export interface TypingDotProps extends StyledComponentProps {
  index: number;
}
