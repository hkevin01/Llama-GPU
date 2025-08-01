import {
    Refresh,
    Save,
    Speed
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Divider,
    FormControl,
    FormControlLabel,
    Grid,
    InputLabel,
    LinearProgress,
    List,
    ListItem,
    ListItemSecondaryAction,
    ListItemText,
    MenuItem,
    Select,
    Switch,
    TextField,
    Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { useAppContext } from '../../context/AppContext';

function MultiGPUConfig() {
  const { state, dispatch } = useAppContext();
  const [gpuUtilization, setGpuUtilization] = useState([]);

  useEffect(() => {
    // Simulate real-time GPU utilization data
    const interval = setInterval(() => {
      const newData = state.systemInfo.gpus.map((gpu, index) => ({
        name: `GPU ${index}`,
        utilization: Math.random() * 100,
        memory: Math.random() * 100,
        temperature: Math.random() * 30 + 40,
      }));
      setGpuUtilization(newData);
    }, 2000);

    return () => clearInterval(interval);
  }, [state.systemInfo.gpus]);

  const handleStrategyChange = (strategy) => {
    dispatch({
      type: 'SET_MULTI_GPU_STRATEGY',
      payload: strategy
    });
  };

  const handleLoadBalancingChange = (method) => {
    dispatch({
      type: 'SET_LOAD_BALANCING',
      payload: method
    });
  };

  const handleGPUToggle = (gpuId) => {
    const currentIds = state.multiGPU.gpuIds;
    const newIds = currentIds.includes(gpuId)
      ? currentIds.filter(id => id !== gpuId)
      : [...currentIds, gpuId];

    dispatch({
      type: 'SET_GPU_IDS',
      payload: newIds
    });
  };

  const handleParallelismChange = (type, value) => {
    dispatch({
      type: 'SET_PARALLELISM_SIZE',
      payload: { type, value }
    });
  };

  const saveConfiguration = () => {
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        title: 'Configuration Saved',
        message: 'Multi-GPU configuration has been saved successfully',
        type: 'success',
        timestamp: new Date().toLocaleTimeString(),
      }
    });
  };

  const refreshGPUStats = () => {
    dispatch({ type: 'REFRESH_GPU_STATS' });
  };

  const getUtilizationColor = (value) => {
    if (value > 80) return '#d32f2f';
    if (value > 60) return '#f57c00';
    return '#388e3c';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Multi-GPU Configuration
      </Typography>

      {state.systemInfo.gpus.length === 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          No GPUs detected. Multi-GPU features require CUDA-compatible GPUs.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* GPU Selection */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                GPU Selection
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={state.multiGPU.enabled}
                    onChange={(e) => dispatch({ type: 'TOGGLE_MULTI_GPU', payload: e.target.checked })}
                  />
                }
                label="Enable Multi-GPU"
                sx={{ mb: 2 }}
              />

              {state.systemInfo.gpus.length > 0 ? (
                <List>
                  {state.systemInfo.gpus.map((gpu, index) => (
                    <ListItem key={index}>
                      <ListItemText
                        primary={`GPU ${index}: ${gpu.name}`}
                        secondary={`${gpu.memoryTotal}MB Memory`}
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          checked={state.multiGPU.gpuIds.includes(index)}
                          onChange={() => handleGPUToggle(index)}
                          disabled={!state.multiGPU.enabled}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No GPUs detected
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Parallelism Strategy */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Parallelism Strategy
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Strategy</InputLabel>
                <Select
                  value={state.multiGPU.strategy}
                  label="Strategy"
                  onChange={(e) => handleStrategyChange(e.target.value)}
                  disabled={!state.multiGPU.enabled}
                >
                  <MenuItem value="tensor">Tensor Parallelism</MenuItem>
                  <MenuItem value="pipeline">Pipeline Parallelism</MenuItem>
                  <MenuItem value="data">Data Parallelism</MenuItem>
                  <MenuItem value="hybrid">Hybrid Parallelism</MenuItem>
                </Select>
              </FormControl>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Tensor Parallel Size"
                    type="number"
                    value={state.multiGPU.tensorParallelSize}
                    onChange={(e) => handleParallelismChange('tensor', parseInt(e.target.value))}
                    disabled={!state.multiGPU.enabled || state.multiGPU.strategy === 'data'}
                    inputProps={{ min: 1, max: 8 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Pipeline Parallel Size"
                    type="number"
                    value={state.multiGPU.pipelineParallelSize}
                    onChange={(e) => handleParallelismChange('pipeline', parseInt(e.target.value))}
                    disabled={!state.multiGPU.enabled || state.multiGPU.strategy === 'tensor'}
                    inputProps={{ min: 1, max: 8 }}
                  />
                </Grid>
              </Grid>

              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {state.multiGPU.strategy === 'tensor' && 'Distributes model layers across GPUs'}
                {state.multiGPU.strategy === 'pipeline' && 'Processes different tokens on different GPUs'}
                {state.multiGPU.strategy === 'data' && 'Replicates model across GPUs for parallel batches'}
                {state.multiGPU.strategy === 'hybrid' && 'Combines tensor and pipeline parallelism'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Load Balancing */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Load Balancing
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Load Balancing Method</InputLabel>
                <Select
                  value={state.multiGPU.loadBalancing}
                  label="Load Balancing Method"
                  onChange={(e) => handleLoadBalancingChange(e.target.value)}
                  disabled={!state.multiGPU.enabled}
                >
                  <MenuItem value="round_robin">Round Robin</MenuItem>
                  <MenuItem value="least_loaded">Least Loaded</MenuItem>
                  <MenuItem value="adaptive">Adaptive</MenuItem>
                </Select>
              </FormControl>

              <Typography variant="body2" color="text.secondary">
                {state.multiGPU.loadBalancing === 'round_robin' && 'Distributes requests evenly across GPUs'}
                {state.multiGPU.loadBalancing === 'least_loaded' && 'Routes to GPU with lowest utilization'}
                {state.multiGPU.loadBalancing === 'adaptive' && 'Dynamically adjusts based on performance'}
              </Typography>

              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Current Throughput
                </Typography>
                <Chip
                  label={`${state.multiGPU.stats.throughput.toFixed(1)} req/s`}
                  color="primary"
                  icon={<Speed />}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* GPU Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  GPU Statistics
                </Typography>
                <Button startIcon={<Refresh />} onClick={refreshGPUStats} size="small">
                  Refresh
                </Button>
              </Box>

              {gpuUtilization.length > 0 ? (
                <List>
                  {gpuUtilization.map((gpu, index) => (
                    <ListItem key={index} sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                      <Box sx={{ width: '100%', mb: 1 }}>
                        <Typography variant="subtitle2">{gpu.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Utilization: {gpu.utilization.toFixed(1)}% |
                          Memory: {gpu.memory.toFixed(1)}% |
                          Temp: {gpu.temperature.toFixed(1)}°C
                        </Typography>
                      </Box>
                      <Box sx={{ width: '100%' }}>
                        <LinearProgress
                          variant="determinate"
                          value={gpu.utilization}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: 'grey.200',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: getUtilizationColor(gpu.utilization),
                            },
                          }}
                        />
                      </Box>
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No GPU data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Real-time Utilization Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Real-time GPU Utilization
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={gpuUtilization}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, '']} />
                    <Bar dataKey="utilization" fill="#1976d2" />
                    <Bar dataKey="memory" fill="#388e3c" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Configuration Summary */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Configuration Summary
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={state.multiGPU.enabled ? 'Enabled' : 'Disabled'}
                    color={state.multiGPU.enabled ? 'success' : 'default'}
                  />
                </Grid>

                <Grid item xs={12} md={3}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Active GPUs
                  </Typography>
                  <Typography variant="body1">
                    {state.multiGPU.gpuIds.length} / {state.systemInfo.gpus.length}
                  </Typography>
                </Grid>

                <Grid item xs={12} md={3}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Strategy
                  </Typography>
                  <Typography variant="body1">
                    {state.multiGPU.strategy.charAt(0).toUpperCase() + state.multiGPU.strategy.slice(1)}
                  </Typography>
                </Grid>

                <Grid item xs={12} md={3}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Load Balancing
                  </Typography>
                  <Typography variant="body1">
                    {state.multiGPU.loadBalancing.replace('_', ' ').charAt(0).toUpperCase() +
                     state.multiGPU.loadBalancing.replace('_', ' ').slice(1)}
                  </Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={saveConfiguration}
                disabled={!state.multiGPU.enabled}
              >
                Save Configuration
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default MultiGPUConfig;
