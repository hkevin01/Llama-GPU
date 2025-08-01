import {
    Api,
    Code,
    NetworkCheck,
    PlayArrow,
    Refresh,
    Security,
    Settings,
    Stop,
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControlLabel,
    Grid,
    List,
    ListItem,
    ListItemSecondaryAction,
    ListItemText,
    Paper,
    Switch,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TextField,
    Typography
} from '@mui/material';
import { useState } from 'react';
import { useAppContext } from '../../context/AppContext';

function APIServer() {
  const { state, dispatch } = useAppContext();
  const [serverConfig, setServerConfig] = useState({
    host: '127.0.0.1',
    port: 8000,
    workers: 4,
    maxRequestSize: 10485760, // 10MB
    timeout: 300,
    enableCors: true,
    enableAuth: true,
    apiKey: 'llama-gpu-api-key',
    rateLimit: 60,
    enableWebsocket: true,
    logLevel: 'INFO',
  });

  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [serverLogs, setServerLogs] = useState([
    { timestamp: '2025-08-01 10:30:15', level: 'INFO', message: 'API server initialized' },
    { timestamp: '2025-08-01 10:30:16', level: 'INFO', message: 'CORS middleware enabled' },
    { timestamp: '2025-08-01 10:30:16', level: 'INFO', message: 'Authentication middleware enabled' },
    { timestamp: '2025-08-01 10:30:17', level: 'INFO', message: 'WebSocket support enabled' },
  ]);

  const startServer = () => {
    dispatch({ type: 'SET_API_SERVER_STATUS', payload: 'connecting' });

    // Simulate server startup
    setTimeout(() => {
      dispatch({ type: 'SET_API_SERVER_STATUS', payload: 'connected' });
      dispatch({
        type: 'ADD_NOTIFICATION',
        payload: {
          title: 'API Server Started',
          message: `Server running on http://${serverConfig.host}:${serverConfig.port}`,
          type: 'success',
          timestamp: new Date().toLocaleTimeString(),
        }
      });

      const newLog = {
        timestamp: new Date().toLocaleString(),
        level: 'INFO',
        message: `API server started on ${serverConfig.host}:${serverConfig.port}`,
      };
      setServerLogs(prev => [...prev, newLog]);
    }, 2000);
  };

  const stopServer = () => {
    dispatch({ type: 'SET_API_SERVER_STATUS', payload: 'disconnected' });
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        title: 'API Server Stopped',
        message: 'API server has been shut down',
        type: 'info',
        timestamp: new Date().toLocaleTimeString(),
      }
    });

    const newLog = {
      timestamp: new Date().toLocaleString(),
      level: 'INFO',
      message: 'API server stopped',
    };
    setServerLogs(prev => [...prev, newLog]);
  };

  const restartServer = () => {
    stopServer();
    setTimeout(() => startServer(), 1000);
  };

  const handleConfigChange = (key, value) => {
    setServerConfig(prev => ({ ...prev, [key]: value }));
  };

  const saveConfiguration = () => {
    setConfigDialogOpen(false);
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        title: 'Configuration Saved',
        message: 'API server configuration has been updated',
        type: 'success',
        timestamp: new Date().toLocaleTimeString(),
      }
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return 'success';
      case 'connecting': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const endpoints = [
    { method: 'POST', path: '/v1/completions', description: 'Text completion' },
    { method: 'POST', path: '/v1/chat/completions', description: 'Chat completion' },
    { method: 'POST', path: '/v1/models/load', description: 'Load model' },
    { method: 'GET', path: '/v1/models', description: 'List models' },
    { method: 'POST', path: '/v1/multi-gpu/config', description: 'Configure multi-GPU' },
    { method: 'GET', path: '/v1/multi-gpu/stats', description: 'GPU statistics' },
    { method: 'POST', path: '/v1/quantization/config', description: 'Quantization settings' },
    { method: 'GET', path: '/v1/quantization/stats', description: 'Quantization statistics' },
    { method: 'GET', path: '/v1/monitor/queues', description: 'Queue monitoring' },
    { method: 'GET', path: '/v1/monitor/batches', description: 'Batch monitoring' },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        API Server Control
      </Typography>

      <Grid container spacing={3}>
        {/* Server Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Server Status
              </Typography>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <Chip
                  label={state.systemInfo.apiServerStatus.charAt(0).toUpperCase() + state.systemInfo.apiServerStatus.slice(1)}
                  color={getStatusColor(state.systemInfo.apiServerStatus)}
                  icon={<Api />}
                />

                {state.systemInfo.apiServerStatus === 'connected' && (
                  <Typography variant="body2" color="text.secondary">
                    Running on {serverConfig.host}:{serverConfig.port}
                  </Typography>
                )}
              </Box>

              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={startServer}
                  disabled={state.systemInfo.apiServerStatus === 'connected' || state.systemInfo.apiServerStatus === 'connecting'}
                  color="success"
                >
                  Start
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<Stop />}
                  onClick={stopServer}
                  disabled={state.systemInfo.apiServerStatus === 'disconnected'}
                  color="error"
                >
                  Stop
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={restartServer}
                  disabled={state.systemInfo.apiServerStatus === 'disconnected'}
                >
                  Restart
                </Button>
              </Box>

              <Button
                variant="outlined"
                startIcon={<Settings />}
                onClick={() => setConfigDialogOpen(true)}
                fullWidth
              >
                Configure Server
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Server Configuration Overview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Configuration
              </Typography>

              <List dense>
                <ListItem>
                  <ListItemText
                    primary="Host & Port"
                    secondary={`${serverConfig.host}:${serverConfig.port}`}
                  />
                </ListItem>

                <ListItem>
                  <ListItemText
                    primary="Workers"
                    secondary={`${serverConfig.workers} processes`}
                  />
                </ListItem>

                <ListItem>
                  <ListItemText
                    primary="Authentication"
                    secondary={serverConfig.enableAuth ? 'Enabled' : 'Disabled'}
                  />
                  <ListItemSecondaryAction>
                    <Chip
                      label={serverConfig.enableAuth ? 'ON' : 'OFF'}
                      color={serverConfig.enableAuth ? 'success' : 'default'}
                      size="small"
                    />
                  </ListItemSecondaryAction>
                </ListItem>

                <ListItem>
                  <ListItemText
                    primary="CORS"
                    secondary={serverConfig.enableCors ? 'Enabled' : 'Disabled'}
                  />
                  <ListItemSecondaryAction>
                    <Chip
                      label={serverConfig.enableCors ? 'ON' : 'OFF'}
                      color={serverConfig.enableCors ? 'success' : 'default'}
                      size="small"
                    />
                  </ListItemSecondaryAction>
                </ListItem>

                <ListItem>
                  <ListItemText
                    primary="WebSocket"
                    secondary={serverConfig.enableWebsocket ? 'Enabled' : 'Disabled'}
                  />
                  <ListItemSecondaryAction>
                    <Chip
                      label={serverConfig.enableWebsocket ? 'ON' : 'OFF'}
                      color={serverConfig.enableWebsocket ? 'success' : 'default'}
                      size="small"
                    />
                  </ListItemSecondaryAction>
                </ListItem>

                <ListItem>
                  <ListItemText
                    primary="Rate Limit"
                    secondary={`${serverConfig.rateLimit} requests/minute`}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* API Endpoints */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Available API Endpoints
              </Typography>

              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Method</strong></TableCell>
                      <TableCell><strong>Endpoint</strong></TableCell>
                      <TableCell><strong>Description</strong></TableCell>
                      <TableCell><strong>Status</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {endpoints.map((endpoint, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Chip
                            label={endpoint.method}
                            color={endpoint.method === 'GET' ? 'primary' : 'secondary'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {endpoint.path}
                          </Typography>
                        </TableCell>
                        <TableCell>{endpoint.description}</TableCell>
                        <TableCell>
                          <Chip
                            label={state.systemInfo.apiServerStatus === 'connected' ? 'Available' : 'Offline'}
                            color={state.systemInfo.apiServerStatus === 'connected' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {state.systemInfo.apiServerStatus === 'connected' && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  API documentation is available at:
                  <code style={{ marginLeft: 8 }}>
                    http://{serverConfig.host}:{serverConfig.port}/docs
                  </code>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Server Logs */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Server Logs
              </Typography>

              <Paper
                sx={{
                  p: 1,
                  height: 300,
                  overflow: 'auto',
                  backgroundColor: 'grey.50',
                  fontFamily: 'monospace',
                  fontSize: '0.75rem',
                }}
              >
                {serverLogs.map((log, index) => (
                  <Box key={index} sx={{ mb: 0.5 }}>
                    <Typography
                      component="span"
                      color="text.secondary"
                      sx={{ fontSize: 'inherit' }}
                    >
                      {log.timestamp}
                    </Typography>
                    <Typography
                      component="span"
                      color={log.level === 'ERROR' ? 'error.main' : log.level === 'WARN' ? 'warning.main' : 'text.primary'}
                      sx={{ mx: 1, fontSize: 'inherit' }}
                    >
                      [{log.level}]
                    </Typography>
                    <Typography
                      component="span"
                      sx={{ fontSize: 'inherit' }}
                    >
                      {log.message}
                    </Typography>
                  </Box>
                ))}
              </Paper>
            </CardContent>
          </Card>
        </Grid>

        {/* Security Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Security & Authentication
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" gutterBottom>
                    API Key Authentication
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Current API Key: <code>{serverConfig.apiKey}</code>
                  </Typography>
                  <Button variant="outlined" size="small" startIcon={<Security />}>
                    Regenerate Key
                  </Button>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" gutterBottom>
                    Rate Limiting
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {serverConfig.rateLimit} requests per minute per API key
                  </Typography>
                  <Button variant="outlined" size="small" startIcon={<NetworkCheck />}>
                    View Limits
                  </Button>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" gutterBottom>
                    CORS Configuration
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {serverConfig.enableCors ? 'Allow all origins' : 'Disabled'}
                  </Typography>
                  <Button variant="outlined" size="small" startIcon={<Code />}>
                    Configure
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Configuration Dialog */}
      <Dialog open={configDialogOpen} onClose={() => setConfigDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Server Configuration</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Host"
                value={serverConfig.host}
                onChange={(e) => handleConfigChange('host', e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Port"
                type="number"
                value={serverConfig.port}
                onChange={(e) => handleConfigChange('port', parseInt(e.target.value))}
                margin="normal"
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Workers"
                type="number"
                value={serverConfig.workers}
                onChange={(e) => handleConfigChange('workers', parseInt(e.target.value))}
                margin="normal"
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Rate Limit (req/min)"
                type="number"
                value={serverConfig.rateLimit}
                onChange={(e) => handleConfigChange('rateLimit', parseInt(e.target.value))}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API Key"
                value={serverConfig.apiKey}
                onChange={(e) => handleConfigChange('apiKey', e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={serverConfig.enableAuth}
                    onChange={(e) => handleConfigChange('enableAuth', e.target.checked)}
                  />
                }
                label="Enable Authentication"
              />
            </Grid>
            <Grid item xs={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={serverConfig.enableCors}
                    onChange={(e) => handleConfigChange('enableCors', e.target.checked)}
                  />
                }
                label="Enable CORS"
              />
            </Grid>
            <Grid item xs={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={serverConfig.enableWebsocket}
                    onChange={(e) => handleConfigChange('enableWebsocket', e.target.checked)}
                  />
                }
                label="Enable WebSocket"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Cancel</Button>
          <Button onClick={saveConfiguration} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default APIServer;
