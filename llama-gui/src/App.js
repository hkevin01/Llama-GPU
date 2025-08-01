import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';

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
import { AppProvider } from './context/AppContext';
import { WebSocketProvider } from './context/WebSocketContext';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#3b82f6',
      light: '#60a5fa',
      dark: '#2563eb',
    },
    secondary: {
      main: '#8b5cf6',
      light: '#a78bfa',
      dark: '#7c3aed',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
    text: {
      primary: '#1e293b',
      secondary: '#64748b',
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
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
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
  },
});

function App() {
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    // Simulate initialization
    const timer = setTimeout(() => {
      setLoading(false);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  if (loading) {
    return <LoadingSpinner message="Initializing Llama-GPU Interface..." />;
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppProvider>
        <WebSocketProvider>
          <Router>
            <div className="flex h-screen bg-gray-50">
              <AnimatePresence>
                {sidebarOpen && (
                  <motion.div
                    initial={{ x: -300 }}
                    animate={{ x: 0 }}
                    exit={{ x: -300 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    className="flex-shrink-0"
                  >
                    <Sidebar onClose={() => setSidebarOpen(false)} />
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="flex-1 flex flex-col overflow-hidden">
                <Header
                  onToggleSidebar={toggleSidebar}
                  onToggleDarkMode={toggleDarkMode}
                  sidebarOpen={sidebarOpen}
                  darkMode={darkMode}
                />

                <main className="flex-1 overflow-auto">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="h-full"
                  >
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/models" element={<ModelManager />} />
                      <Route path="/inference" element={<InferenceCenter />} />
                      <Route path="/multi-gpu" element={<MultiGPUConfig />} />
                      <Route path="/quantization" element={<QuantizationSettings />} />
                      <Route path="/performance" element={<PerformanceMonitor />} />
                      <Route path="/api-server" element={<APIServer />} />
                      <Route path="/settings" element={<Settings />} />
                    </Routes>
                  </motion.div>
                </main>
              </div>

              <NotificationSystem />
            </div>
          </Router>
        </WebSocketProvider>
      </AppProvider>
    </ThemeProvider>
  );
}

export default App;
