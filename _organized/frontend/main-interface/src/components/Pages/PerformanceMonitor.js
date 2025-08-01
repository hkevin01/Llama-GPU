import {
    Computer,
    Download,
    Memory,
    Psychology,
    Refresh,
    Speed
} from '@mui/icons-material';
import {
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Grid,
    IconButton,
    LinearProgress,
    List,
    ListItem,
    ListItemText,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography
} from '@mui/material';
import { useEffect, useState } from 'react';
import {
    CartesianGrid,
    Line,
    LineChart,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    XAxis,
    YAxis
} from 'recharts';
import { useAppContext } from '../../context/AppContext';

function PerformanceMonitor() {
  const { state, dispatch } = useAppContext();
  const [performanceHistory, setPerformanceHistory] = useState([]);
  const [gpuMetrics, setGpuMetrics] = useState([]);
  const [systemMetrics, setSystemMetrics] = useState({
    cpuUsage: 0,
    ramUsage: 0,
    diskUsage: 0,
    networkIO: 0,
  });

  useEffect(() => {
    // Simulate real-time performance data
    const interval = setInterval(() => {
      const newDataPoint = {
        time: new Date().toLocaleTimeString(),
        tokensPerSecond: Math.random() * 50 + 10,
        requestsPerSecond: Math.random() * 20 + 5,
        latency: Math.random() * 100 + 50,
        queueLength: Math.floor(Math.random() * 10),
        gpuUtilization: Math.random() * 80 + 20,
        memoryUsage: Math.random() * 30 + 60,
      };

      setPerformanceHistory(prev => [...prev.slice(-19), newDataPoint]);

      // Update GPU metrics
      const newGpuMetrics = state.systemInfo.gpus.map((gpu, index) => ({
        id: index,
        name: gpu.name,
        utilization: Math.random() * 100,
        memory: Math.random() * 100,
        temperature: Math.random() * 30 + 40,
        powerUsage: Math.random() * 200 + 100,
      }));
      setGpuMetrics(newGpuMetrics);

      // Update system metrics
      setSystemMetrics({
        cpuUsage: Math.random() * 80 + 10,
        ramUsage: Math.random() * 70 + 20,
        diskUsage: Math.random() * 50 + 30,
        networkIO: Math.random() * 1000 + 100,
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [state.systemInfo.gpus]);

  const refreshMetrics = () => {
    dispatch({ type: 'REFRESH_PERFORMANCE_METRICS' });
  };

  const exportMetrics = () => {
    const data = {
      timestamp: new Date().toISOString(),
      performanceHistory,
      gpuMetrics,
      systemMetrics,
      inferenceStats: state.inference.stats,
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `llama-gpu-metrics-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getUtilizationColor = (value) => {
    if (value > 80) return 'error';
    if (value > 60) return 'warning';
    return 'success';
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Performance Monitor
        </Typography>
        <Box>
          <Button startIcon={<Download />} onClick={exportMetrics} sx={{ mr: 1 }}>
            Export
          </Button>
          <IconButton onClick={refreshMetrics} color="primary">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Key Performance Indicators */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Speed color="primary" sx={{ fontSize: 40 }} />
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="h4" fontWeight="bold" color="primary">
                    {state.inference.stats.avgTokensPerSecond.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Tokens/sec
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Psychology color="success" sx={{ fontSize: 40 }} />
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="h4" fontWeight="bold" color="success.main">
                    {state.inference.activeRequests.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Requests
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Memory color="warning" sx={{ fontSize: 40 }} />
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="h4" fontWeight="bold" color="warning.main">
                    {systemMetrics.ramUsage.toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Memory Usage
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Computer color="error" sx={{ fontSize: 40 }} />
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="h4" fontWeight="bold" color="error.main">
                    {systemMetrics.cpuUsage.toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    CPU Usage
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Real-time Performance Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Real-time Performance Metrics
              </Typography>
              <Box sx={{ height: 350 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={performanceHistory}>
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
                      dataKey="requestsPerSecond"
                      stroke="#388e3c"
                      strokeWidth={2}
                      name="Requests/sec"
                    />
                    <Line
                      type="monotone"
                      dataKey="latency"
                      stroke="#f57c00"
                      strokeWidth={2}
                      name="Latency (ms)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Resources */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Resources
              </Typography>

              <List>
                <ListItem>
                  <ListItemText
                    primary="CPU Usage"
                    secondary={`${systemMetrics.cpuUsage.toFixed(1)}%`}
                  />
                  <LinearProgress
                    variant="determinate"
                    value={systemMetrics.cpuUsage}
                    color={getUtilizationColor(systemMetrics.cpuUsage)}
                    sx={{ width: 100, ml: 2 }}
                  />
                </ListItem>

                <ListItem>
                  <ListItemText
                    primary="RAM Usage"
                    secondary={`${systemMetrics.ramUsage.toFixed(1)}%`}
                  />
                  <LinearProgress
                    variant="determinate"
                    value={systemMetrics.ramUsage}
                    color={getUtilizationColor(systemMetrics.ramUsage)}
                    sx={{ width: 100, ml: 2 }}
                  />
                </ListItem>

                <ListItem>
                  <ListItemText
                    primary="Disk Usage"
                    secondary={`${systemMetrics.diskUsage.toFixed(1)}%`}
                  />
                  <LinearProgress
                    variant="determinate"
                    value={systemMetrics.diskUsage}
                    color={getUtilizationColor(systemMetrics.diskUsage)}
                    sx={{ width: 100, ml: 2 }}
                  />
                </ListItem>

                <ListItem>
                  <ListItemText
                    primary="Network I/O"
                    secondary={formatBytes(systemMetrics.networkIO * 1024)}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* GPU Metrics */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                GPU Performance
              </Typography>

              {gpuMetrics.length > 0 ? (
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell><strong>GPU</strong></TableCell>
                        <TableCell align="right"><strong>Utilization</strong></TableCell>
                        <TableCell align="right"><strong>Memory</strong></TableCell>
                        <TableCell align="right"><strong>Temperature</strong></TableCell>
                        <TableCell align="right"><strong>Power</strong></TableCell>
                        <TableCell align="right"><strong>Status</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {gpuMetrics.map((gpu) => (
                        <TableRow key={gpu.id}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              GPU {gpu.id}: {gpu.name}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                              <Typography variant="body2" sx={{ mr: 1 }}>
                                {gpu.utilization.toFixed(1)}%
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={gpu.utilization}
                                color={getUtilizationColor(gpu.utilization)}
                                sx={{ width: 60 }}
                              />
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                              <Typography variant="body2" sx={{ mr: 1 }}>
                                {gpu.memory.toFixed(1)}%
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={gpu.memory}
                                color={getUtilizationColor(gpu.memory)}
                                sx={{ width: 60 }}
                              />
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2">
                              {gpu.temperature.toFixed(0)}°C
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2">
                              {gpu.powerUsage.toFixed(0)}W
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Chip
                              label={gpu.utilization > 10 ? 'Active' : 'Idle'}
                              color={gpu.utilization > 10 ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No GPU data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Inference Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Inference Statistics
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Requests
                  </Typography>
                  <Typography variant="h6">
                    {state.inference.stats.totalRequests}
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Success Rate
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    {((state.inference.stats.successfulRequests / Math.max(state.inference.stats.totalRequests, 1)) * 100).toFixed(1)}%
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Avg Response Time
                  </Typography>
                  <Typography variant="h6">
                    {state.inference.stats.avgResponseTime.toFixed(0)}ms
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Queue Length
                  </Typography>
                  <Typography variant="h6">
                    {performanceHistory.length > 0 ? performanceHistory[performanceHistory.length - 1].queueLength : 0}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Batch Processing Stats */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Batch Processing
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Batches Processed
                  </Typography>
                  <Typography variant="h6">
                    {state.inference.stats.batchesProcessed || 0}
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Avg Batch Size
                  </Typography>
                  <Typography variant="h6">
                    {state.inference.stats.avgBatchSize || 0}
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Batch Throughput
                  </Typography>
                  <Typography variant="h6">
                    {state.inference.stats.batchThroughput?.toFixed(1) || '0.0'} req/s
                  </Typography>
                </Grid>

                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Processing Time
                  </Typography>
                  <Typography variant="h6">
                    {state.inference.stats.avgBatchProcessingTime?.toFixed(0) || '0'}ms
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default PerformanceMonitor;
