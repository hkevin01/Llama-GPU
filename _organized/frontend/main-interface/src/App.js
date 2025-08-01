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

// App Layout component that uses context
function AppLayout() {
  const { state } = useAppContext();
  const { ui } = state;

  // Create dynamic theme based on context
  const theme = createTheme({
    palette: {
      mode: ui.theme,
      primary: {
        main: ui.theme === 'dark' ? '#90caf9' : '#3b82f6',
        light: ui.theme === 'dark' ? '#bbdefb' : '#60a5fa',
        dark: ui.theme === 'dark' ? '#64b5f6' : '#2563eb',
      },
      secondary: {
        main: ui.theme === 'dark' ? '#f48fb1' : '#8b5cf6',
        light: ui.theme === 'dark' ? '#f8bbd9' : '#a78bfa',
        dark: ui.theme === 'dark' ? '#f06292' : '#7c3aed',
      },
      background: {
        default: ui.theme === 'dark' ? '#121212' : '#f8fafc',
        paper: ui.theme === 'dark' ? '#1e1e1e' : '#ffffff',
      },
      text: {
        primary: ui.theme === 'dark' ? '#ffffff' : '#1e293b',
        secondary: ui.theme === 'dark' ? '#b3b3b3' : '#64748b',
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
            boxShadow: ui.theme === 'dark'
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
  });

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
