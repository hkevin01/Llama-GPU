import { Box } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';

// Components
import LoadingSpinner from './components/Common/LoadingSpinner';
import NotificationSystem from './components/Common/NotificationSystem';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import APIServer from './components/Pages/APIServer';
import Dashboard from './components/Pages/Dashboard';
import InferenceCenter from './components/Pages/InferenceCenter';
import ModelManager from './components/Pages/ModelManager';
import MultiGPUConfig from './components/Pages/MultiGPUConfig';
import PerformanceMonitor from './components/Pages/PerformanceMonitor';
import QuantizationSettings from './components/Pages/QuantizationSettings';
import Settings from './components/Pages/Settings';

// Context
import { AppProvider, useAppContext } from './context/AppContext';

// Theme validation utility
const validateTheme = (theme) => {
  const requiredPalettes = ['primary', 'secondary', 'success', 'warning', 'error', 'info', 'grey'];
  const missingPalettes = requiredPalettes.filter(palette => !theme.palette[palette]);

  if (missingPalettes.length > 0) {
    console.warn('Missing theme palettes:', missingPalettes);
  }

  // Check for 'main' property in each palette
  requiredPalettes.forEach(palette => {
    if (theme.palette[palette] && !theme.palette[palette].main) {
      console.warn(`Missing 'main' property in ${palette} palette`);
    }
  });

  return theme;
};

// App Layout component that uses context
function AppLayout() {
  const { state } = useAppContext();
  const { ui } = state;

  // Create dynamic theme based on context
  const theme = validateTheme(createTheme({
    palette: {
      mode: ui.darkMode ? 'dark' : 'light',
      primary: {
        main: ui.darkMode ? '#90caf9' : '#3b82f6',
        light: ui.darkMode ? '#bbdefb' : '#60a5fa',
        dark: ui.darkMode ? '#64b5f6' : '#2563eb',
      },
      secondary: {
        main: ui.darkMode ? '#f48fb1' : '#8b5cf6',
        light: ui.darkMode ? '#f8bbd9' : '#a78bfa',
        dark: ui.darkMode ? '#f06292' : '#7c3aed',
      },
      success: {
        main: ui.darkMode ? '#4caf50' : '#10b981',
        light: ui.darkMode ? '#81c784' : '#34d399',
        dark: ui.darkMode ? '#388e3c' : '#059669',
      },
      warning: {
        main: ui.darkMode ? '#ff9800' : '#f59e0b',
        light: ui.darkMode ? '#ffb74d' : '#fbbf24',
        dark: ui.darkMode ? '#f57c00' : '#d97706',
      },
      error: {
        main: ui.darkMode ? '#f44336' : '#ef4444',
        light: ui.darkMode ? '#e57373' : '#f87171',
        dark: ui.darkMode ? '#d32f2f' : '#dc2626',
      },
      info: {
        main: ui.darkMode ? '#2196f3' : '#3b82f6',
        light: ui.darkMode ? '#64b5f6' : '#60a5fa',
        dark: ui.darkMode ? '#1976d2' : '#2563eb',
      },
      grey: {
        50: ui.darkMode ? '#fafafa' : '#f9fafb',
        100: ui.darkMode ? '#f5f5f5' : '#f3f4f6',
        200: ui.darkMode ? '#eeeeee' : '#e5e7eb',
        300: ui.darkMode ? '#e0e0e0' : '#d1d5db',
        400: ui.darkMode ? '#bdbdbd' : '#9ca3af',
        500: ui.darkMode ? '#9e9e9e' : '#6b7280',
        600: ui.darkMode ? '#757575' : '#4b5563',
        700: ui.darkMode ? '#616161' : '#374151',
        800: ui.darkMode ? '#424242' : '#1f2937',
        900: ui.darkMode ? '#212121' : '#111827',
      },
      background: {
        default: ui.darkMode ? '#121212' : '#f8fafc',
        paper: ui.darkMode ? '#1e1e1e' : '#ffffff',
      },
      text: {
        primary: ui.darkMode ? '#ffffff' : '#1e293b',
        secondary: ui.darkMode ? '#b3b3b3' : '#64748b',
      },
    },
    typography: {
      fontFamily: 'Inter, sans-serif',
      h4: {
        fontWeight: 600,
      },
      h5: {
        fontWeight: 600,
      },
      h6: {
        fontWeight: 600,
      },
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: '8px',
            fontWeight: 500,
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: '12px',
            boxShadow: ui.darkMode
              ? '0 1px 3px 0 rgba(255, 255, 255, 0.1), 0 1px 2px 0 rgba(255, 255, 255, 0.06)'
              : '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: '12px',
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            borderRight: 'none',
          },
        },
      },
    },
  }));

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh' }}>
        <Header />
        <Sidebar />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            mt: '64px', // Header height
            ml: ui.sidebarCollapsed ? '60px' : '280px',
            transition: 'margin-left 0.3s ease',
            p: 3,
            overflow: 'auto',
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            style={{ height: '100%' }}
          >
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/models" element={<ModelManager />} />
              <Route path="/inference" element={<InferenceCenter />} />
              <Route path="/multi-gpu" element={<MultiGPUConfig />} />
              <Route path="/quantization" element={<QuantizationSettings />} />
              <Route path="/performance" element={<PerformanceMonitor />} />
              <Route path="/api-server" element={<APIServer />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </motion.div>
        </Box>
        <NotificationSystem />
      </Box>
    </ThemeProvider>
  );
}

function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate initialization
    const timer = setTimeout(() => {
      setLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return <LoadingSpinner message="Initializing Llama-GPU Interface..." />;
  }

  return (
    <AppProvider>
      <Router>
        <AppLayout />
      </Router>
    </AppProvider>
  );
}

export default App;
