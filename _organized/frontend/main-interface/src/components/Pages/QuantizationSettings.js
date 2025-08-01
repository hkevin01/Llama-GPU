import {
    Save,
    TrendingDown,
    TrendingUp
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
    List,
    ListItem,
    ListItemText,
    MenuItem,
    Paper,
    Select,
    Switch,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Typography
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { useAppContext } from '../../context/AppContext';

function QuantizationSettings() {
  const { state, dispatch } = useAppContext();
  const [memoryComparison, setMemoryComparison] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);

  useEffect(() => {
    // Simulate memory usage comparison data
    const baseMemory = 4000; // MB
    const reductions = {
      'fp32': 0,
      'fp16': 50,
      'bf16': 50,
      'int8': 75,
      'int4': 87.5,
    };

    const comparisonData = Object.entries(reductions).map(([type, reduction]) => ({
      type: type.toUpperCase(),
      memory: baseMemory * (1 - reduction / 100),
      reduction: reduction,
      accuracy: type === 'fp32' ? 100 : Math.max(85, 100 - reduction * 0.2),
    }));

    setMemoryComparison(comparisonData);

    // Simulate performance metrics
    const perfData = Object.entries(reductions).map(([type, reduction]) => ({
      type: type.toUpperCase(),
      speed: 1 + reduction * 0.02, // Speed improvement factor
      latency: Math.max(50, 200 - reduction * 2), // ms
    }));

    setPerformanceData(perfData);
  }, []);

  const handleQuantizationToggle = (enabled) => {
    dispatch({
      type: 'TOGGLE_QUANTIZATION',
      payload: enabled
    });
  };

  const handleQuantizationTypeChange = (type) => {
    dispatch({
      type: 'SET_QUANTIZATION_TYPE',
      payload: type
    });
  };

  const handleDynamicToggle = (dynamic) => {
    dispatch({
      type: 'SET_QUANTIZATION_DYNAMIC',
      payload: dynamic
    });
  };

  const handleMemoryEfficientToggle = (enabled) => {
    dispatch({
      type: 'SET_QUANTIZATION_MEMORY_EFFICIENT',
      payload: enabled
    });
  };

  const handleAccuracyPreservationToggle = (enabled) => {
    dispatch({
      type: 'SET_QUANTIZATION_PRESERVE_ACCURACY',
      payload: enabled
    });
  };

  const saveConfiguration = () => {
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        title: 'Quantization Settings Saved',
        message: `Configuration saved with ${state.quantization.type.toUpperCase()} quantization`,
        type: 'success',
        timestamp: new Date().toLocaleTimeString(),
      }
    });
  };

  const getQuantizationColor = (type) => {
    const colors = {
      'int4': '#d32f2f',
      'int8': '#f57c00',
      'fp16': '#388e3c',
      'bf16': '#1976d2',
      'fp32': '#7b1fa2',
    };
    return colors[type.toLowerCase()] || '#757575';
  };

  const COLORS = ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2'];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Quantization Settings
      </Typography>

      <Grid container spacing={3}>
        {/* Main Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quantization Configuration
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={state.quantization.enabled}
                    onChange={(e) => handleQuantizationToggle(e.target.checked)}
                  />
                }
                label="Enable Quantization"
                sx={{ mb: 3 }}
              />

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Quantization Type</InputLabel>
                <Select
                  value={state.quantization.type}
                  label="Quantization Type"
                  onChange={(e) => handleQuantizationTypeChange(e.target.value)}
                  disabled={!state.quantization.enabled}
                >
                  <MenuItem value="int4">INT4 (Maximum Compression)</MenuItem>
                  <MenuItem value="int8">INT8 (Balanced)</MenuItem>
                  <MenuItem value="fp16">FP16 (Half Precision)</MenuItem>
                  <MenuItem value="bf16">BF16 (Brain Float)</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={state.quantization.dynamic}
                    onChange={(e) => handleDynamicToggle(e.target.checked)}
                    disabled={!state.quantization.enabled}
                  />
                }
                label="Dynamic Quantization"
                sx={{ display: 'block', mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={state.quantization.memoryEfficient}
                    onChange={(e) => handleMemoryEfficientToggle(e.target.checked)}
                    disabled={!state.quantization.enabled}
                  />
                }
                label="Memory Efficient Mode"
                sx={{ display: 'block', mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={state.quantization.preserveAccuracy}
                    onChange={(e) => handleAccuracyPreservationToggle(e.target.checked)}
                    disabled={!state.quantization.enabled}
                  />
                }
                label="Accuracy Preservation"
                sx={{ display: 'block', mb: 3 }}
              />

              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={saveConfiguration}
                disabled={!state.quantization.enabled}
                fullWidth
              >
                Apply Configuration
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Current Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Status
              </Typography>

              <List>
                <ListItem>
                  <ListItemText
                    primary="Quantization Status"
                    secondary={
                      <Chip
                        label={state.quantization.enabled ? 'Active' : 'Disabled'}
                        color={state.quantization.enabled ? 'success' : 'default'}
                        size="small"
                      />
                    }
                  />
                </ListItem>

                {state.quantization.enabled && (
                  <>
                    <ListItem>
                      <ListItemText
                        primary="Current Type"
                        secondary={
                          <Chip
                            label={state.quantization.type.toUpperCase()}
                            style={{ backgroundColor: getQuantizationColor(state.quantization.type), color: 'white' }}
                            size="small"
                          />
                        }
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemText
                        primary="Mode"
                        secondary={state.quantization.dynamic ? 'Dynamic' : 'Static'}
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemText
                        primary="Memory Optimization"
                        secondary={state.quantization.memoryEfficient ? 'Enabled' : 'Disabled'}
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemText
                        primary="Accuracy Preservation"
                        secondary={state.quantization.preserveAccuracy ? 'Enabled' : 'Disabled'}
                      />
                    </ListItem>
                  </>
                )}
              </List>

              {state.quantization.enabled && state.models.loaded && (
                <Box sx={{ mt: 2 }}>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Model Impact
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <TrendingDown color="success" />
                    <Typography variant="body2">
                      Memory: ~{Math.round(memoryComparison.find(item =>
                        item.type.toLowerCase() === state.quantization.type)?.reduction || 0)}% reduction
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TrendingUp color="primary" />
                    <Typography variant="body2">
                      Speed: ~{((performanceData.find(item =>
                        item.type.toLowerCase() === state.quantization.type)?.speed || 1) - 1) * 100}% faster
                    </Typography>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Memory Usage Comparison */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Memory Usage Comparison
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={memoryComparison}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="type" />
                    <YAxis label={{ value: 'Memory (MB)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip formatter={(value, name) => [
                      name === 'memory' ? `${value.toFixed(0)} MB` : `${value.toFixed(1)}%`,
                      name === 'memory' ? 'Memory Usage' : 'Reduction'
                    ]} />
                    <Bar dataKey="memory" fill="#1976d2" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Impact */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Impact
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={memoryComparison}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="reduction"
                      label={({ type, reduction }) => `${type}: ${reduction}%`}
                    >
                      {memoryComparison.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value}%`, 'Memory Reduction']} />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Detailed Comparison Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detailed Comparison
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Type</strong></TableCell>
                      <TableCell align="right"><strong>Memory Usage (MB)</strong></TableCell>
                      <TableCell align="right"><strong>Memory Reduction (%)</strong></TableCell>
                      <TableCell align="right"><strong>Accuracy (%)</strong></TableCell>
                      <TableCell align="right"><strong>Speed Factor</strong></TableCell>
                      <TableCell align="right"><strong>Latency (ms)</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {memoryComparison.map((row, index) => (
                      <TableRow key={row.type}>
                        <TableCell>
                          <Chip
                            label={row.type}
                            style={{
                              backgroundColor: row.type.toLowerCase() === state.quantization.type && state.quantization.enabled
                                ? getQuantizationColor(row.type)
                                : 'default',
                              color: row.type.toLowerCase() === state.quantization.type && state.quantization.enabled
                                ? 'white'
                                : 'inherit'
                            }}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">{row.memory.toFixed(0)}</TableCell>
                        <TableCell align="right">{row.reduction}%</TableCell>
                        <TableCell align="right">{row.accuracy.toFixed(1)}%</TableCell>
                        <TableCell align="right">{performanceData[index]?.speed.toFixed(2)}x</TableCell>
                        <TableCell align="right">{performanceData[index]?.latency.toFixed(0)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recommendations
              </Typography>

              {!state.quantization.enabled ? (
                <Alert severity="info">
                  Enable quantization to reduce memory usage and improve inference speed.
                  Start with INT8 for a good balance between performance and accuracy.
                </Alert>
              ) : (
                <Box>
                  {state.quantization.type === 'int4' && (
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      INT4 quantization provides maximum compression but may significantly impact model accuracy.
                      Consider enabling accuracy preservation features.
                    </Alert>
                  )}

                  {state.quantization.type === 'fp16' && (
                    <Alert severity="success" sx={{ mb: 2 }}>
                      FP16 provides good performance improvements with minimal accuracy loss.
                      Ideal for most production workloads.
                    </Alert>
                  )}

                  {!state.quantization.dynamic && (
                    <Alert severity="info">
                      Consider enabling dynamic quantization for better accuracy with minimal performance overhead.
                    </Alert>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default QuantizationSettings;
