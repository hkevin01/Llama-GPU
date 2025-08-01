import {
    Api,
    Memory,
    Psychology,
    Refresh,
    Speed
} from '@mui/icons-material';
import {
    Box,
    Card,
    CardContent,
    Chip,
    Divider,
    Grid,
    IconButton,
    LinearProgress,
    List,
    ListItem,
    ListItemText,
    Tooltip,
    Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { CartesianGrid, Line, LineChart, Tooltip as RechartsTooltip, ResponsiveContainer, XAxis, YAxis } from 'recharts';
import { useAppContext } from '../../context/AppContext';

function Dashboard() {
  const { state, dispatch } = useAppContext();
  const [performanceData, setPerformanceData] = useState([]);

  useEffect(() => {
    // Simulate real-time performance data
    const interval = setInterval(() => {
      const newPoint = {
        time: new Date().toLocaleTimeString(),
        tokensPerSecond: Math.random() * 50 + 10,
        gpuMemory: Math.random() * 30 + 60,
        cpuUsage: Math.random() * 40 + 20,
        throughput: Math.random() * 10 + 5,
      };

      setPerformanceData(prev => {
        const updated = [...prev, newPoint].slice(-20); // Keep last 20 points
        return updated;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const refreshStats = () => {
    dispatch({ type: 'REFRESH_SYSTEM_STATS' });
  };

  const StatCard = ({ title, value, subtitle, icon: Icon, color, progress }) => (
    <Card sx={{ height: '100%', background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Icon sx={{ color, fontSize: 28 }} />
          <Typography variant="h4" fontWeight="bold" color={color}>
            {value}
          </Typography>
        </Box>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
        {progress !== undefined && (
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ mt: 1, height: 6, borderRadius: 3 }}
            color={progress > 80 ? 'error' : progress > 60 ? 'warning' : 'success'}
          />
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Dashboard
        </Typography>
        <Tooltip title="Refresh Statistics">
          <IconButton onClick={refreshStats} color="primary">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {/* System Statistics */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="GPU Memory"
            value={`${state.systemInfo.memoryUsage}%`}
            subtitle={`${state.systemInfo.gpus.length} GPU${state.systemInfo.gpus.length !== 1 ? 's' : ''} detected`}
            icon={Memory}
            color="#1976d2"
            progress={state.systemInfo.memoryUsage}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Inference Speed"
            value={`${state.inference.stats.avgTokensPerSecond.toFixed(1)}`}
            subtitle="tokens/second"
            icon={Speed}
            color="#388e3c"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Requests"
            value={state.inference.activeRequests.length}
            subtitle={`${state.inference.stats.totalRequests} total processed`}
            icon={Psychology}
            color="#f57c00"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="API Server"
            value={state.systemInfo.apiServerStatus === 'connected' ? 'Online' : 'Offline'}
            subtitle={`${state.systemInfo.backendType} backend`}
            icon={Api}
            color={state.systemInfo.apiServerStatus === 'connected' ? '#388e3c' : '#d32f2f'}
          />
        </Grid>

        {/* Performance Charts */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Real-time Performance
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line
                      type="monotone"
                      dataKey="tokensPerSecond"
                      stroke="#1976d2"
                      strokeWidth={2}
                      name="Tokens/sec"
                    />
                    <Line
                      type="monotone"
                      dataKey="throughput"
                      stroke="#388e3c"
                      strokeWidth={2}
                      name="Throughput"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Overview */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Overview
              </Typography>

              {/* Current Model */}
              {state.models.loaded ? (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Loaded Model
                  </Typography>
                  <Chip
                    label={state.models.loaded.name}
                    color="success"
                    size="small"
                    sx={{ mt: 0.5 }}
                  />
                  <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                    Backend: {state.models.loaded.backend}
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    No Model Loaded
                  </Typography>
                  <Chip label="Idle" color="default" size="small" sx={{ mt: 0.5 }} />
                </Box>
              )}

              <Divider sx={{ my: 2 }} />

              {/* GPU Information */}
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                GPU Status
              </Typography>
              {state.systemInfo.gpus.length > 0 ? (
                state.systemInfo.gpus.map((gpu, index) => (
                  <Box key={index} sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      GPU {index}: {gpu.name}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={gpu.memoryUsed / gpu.memoryTotal * 100}
                      sx={{ height: 4, borderRadius: 2 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {gpu.memoryUsed}MB / {gpu.memoryTotal}MB
                    </Typography>
                  </Box>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No GPUs detected
                </Typography>
              )}

              <Divider sx={{ my: 2 }} />

              {/* Quantization Status */}
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Quantization
              </Typography>
              <Chip
                label={state.quantization.enabled ? `${state.quantization.type.toUpperCase()} Active` : 'Disabled'}
                color={state.quantization.enabled ? 'primary' : 'default'}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List>
                {state.notifications.items.slice(0, 5).map((notification, index) => (
                  <ListItem key={index} divider={index < 4}>
                    <ListItemText
                      primary={notification.title}
                      secondary={notification.message}
                      secondaryTypographyProps={{
                        component: 'div'
                      }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {notification.timestamp}
                    </Typography>
                  </ListItem>
                ))}
                {state.notifications.items.length === 0 && (
                  <ListItem>
                    <ListItemText
                      primary="No recent activity"
                      secondary="System activities will appear here"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
