import {
    Api,
    Chat,
    Dashboard,
    Memory,
    Psychology,
    Settings,
    SmartToy,
    Speed,
    Tune,
} from '@mui/icons-material';
import {
    Box,
    Chip,
    Divider,
    Drawer,
    LinearProgress,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Toolbar,
    Typography,
} from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAppContext } from '../../context/AppContext';

const drawerWidth = 280;

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: Dashboard, color: '#1976d2', path: '/dashboard' },
  { id: 'chat', label: 'Chat Interface', icon: Chat, color: '#00acc1', path: '/chat' },
  { id: 'models', label: 'Model Manager', icon: SmartToy, color: '#388e3c', path: '/models' },
  { id: 'inference', label: 'Inference Center', icon: Psychology, color: '#f57c00', path: '/inference' },
  { id: 'multi-gpu', label: 'Multi-GPU Config', icon: Memory, color: '#7b1fa2', path: '/multi-gpu' },
  { id: 'quantization', label: 'Quantization', icon: Tune, color: '#c2185b', path: '/quantization' },
  { id: 'performance', label: 'Performance Monitor', icon: Speed, color: '#d32f2f', path: '/performance' },
  { id: 'api-server', label: 'API Server', icon: Api, color: '#0288d1', path: '/api-server' },
  { id: 'settings', label: 'Settings', icon: Settings, color: '#455a64', path: '/settings' },
];

function Sidebar() {
  const { state } = useAppContext();
  const navigate = useNavigate();
  const location = useLocation();

  const handlePageChange = (path) => {
    navigate(path);
  };

  const getMemoryUsageColor = (usage) => {
    if (usage > 80) return 'error';
    if (usage > 60) return 'warning';
    return 'success';
  };

  // Get current page based on location
  const currentPath = location.pathname;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          background: (theme) => theme.palette.mode === 'dark'
            ? 'linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%)'
            : 'linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%)',
        },
      }}
    >
      <Toolbar />
      <Box sx={{ overflow: 'auto', p: 2 }}>
        {/* System Status */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            System Status
          </Typography>

          {/* Current Model */}
          {state.models.loaded && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Loaded Model
              </Typography>
              <Chip
                label={state.models.loaded.name || 'Unknown Model'}
                size="small"
                color="success"
                sx={{ width: '100%', mt: 0.5 }}
              />
            </Box>
          )}

          {/* Backend Status */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Backend
            </Typography>
            <Chip
              label={`${state.systemInfo.backendType}${state.systemInfo.awsDetected ? ' (AWS)' : ''}`}
              size="small"
              color={state.systemInfo.backendType === 'ROCm' ? 'primary' : 'default'}
              sx={{ width: '100%', mt: 0.5 }}
            />
          </Box>

          {/* GPU Count */}
          {state.systemInfo.gpus.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                GPUs Available
              </Typography>
              <Chip
                label={`${state.systemInfo.gpus.length} GPU${state.systemInfo.gpus.length > 1 ? 's' : ''}`}
                size="small"
                color="primary"
                sx={{ width: '100%', mt: 0.5 }}
              />
            </Box>
          )}

          {/* Memory Usage */}
          <Box sx={{ mb: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Memory Usage: {state.systemInfo.memoryUsage}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={state.systemInfo.memoryUsage}
              color={getMemoryUsageColor(state.systemInfo.memoryUsage)}
              sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
            />
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Navigation Menu */}
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.id} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                selected={currentPath === item.path}
                onClick={() => handlePageChange(item.path)}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: `${item.color}20`,
                    borderLeft: `4px solid ${item.color}`,
                    '& .MuiListItemIcon-root': {
                      color: item.color,
                    },
                    '& .MuiListItemText-primary': {
                      color: item.color,
                      fontWeight: 600,
                    },
                  },
                  '&:hover': {
                    backgroundColor: `${item.color}10`,
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <item.icon />
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                    fontWeight: currentPath === item.path ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        <Divider sx={{ my: 2 }} />

        {/* Quick Stats */}
        <Box>
          <Typography variant="caption" color="text.secondary" gutterBottom>
            Quick Stats
          </Typography>

          {state.inference.stats.totalRequests > 0 && (
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2">
                Total Requests: {state.inference.stats.totalRequests}
              </Typography>
              <Typography variant="body2">
                Avg Speed: {state.inference.stats.avgTokensPerSecond.toFixed(1)} tokens/s
              </Typography>
            </Box>
          )}

          {state.multiGPU.enabled && (
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2" color="primary">
                Multi-GPU: {state.multiGPU.strategy.toUpperCase()}
              </Typography>
              <Typography variant="body2">
                Throughput: {state.multiGPU.stats.throughput.toFixed(1)} req/s
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Drawer>
  );
}

export default Sidebar;
