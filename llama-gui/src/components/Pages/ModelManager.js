import {
    CloudDownload,
    Info,
    Memory,
    Refresh,
    Speed,
    Storage
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
    FormControl,
    Grid,
    IconButton,
    InputLabel,
    LinearProgress,
    List,
    ListItem,
    ListItemText,
    MenuItem,
    Select,
    TextField,
    Tooltip,
    Typography
} from '@mui/material';
import { useState } from 'react';
import { useAppContext } from '../../context/AppContext';

function ModelManager() {
  const { state, dispatch } = useAppContext();
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedBackend, setSelectedBackend] = useState('CPU');
  const [loadDialogOpen, setLoadDialogOpen] = useState(false);
  const [customModelName, setCustomModelName] = useState('');

  const handleLoadModel = async () => {
    if (!selectedModel && !customModelName) return;

    const modelName = customModelName || selectedModel;

    dispatch({ type: 'SET_MODEL_LOADING', payload: true });

    try {
      // Simulate API call to load model
      setTimeout(() => {
        dispatch({
          type: 'SET_LOADED_MODEL',
          payload: {
            name: modelName,
            backend: selectedBackend,
            size: Math.floor(Math.random() * 5000 + 500), // Random size in MB
            type: 'Causal Language Model',
            loadedAt: new Date().toISOString(),
          }
        });
        dispatch({ type: 'SET_MODEL_LOADING', payload: false });
        dispatch({
          type: 'ADD_NOTIFICATION',
          payload: {
            title: 'Model Loaded',
            message: `${modelName} loaded successfully with ${selectedBackend} backend`,
            type: 'success',
            timestamp: new Date().toLocaleTimeString(),
          }
        });
        setLoadDialogOpen(false);
        setCustomModelName('');
      }, 2000);
    } catch (error) {
      dispatch({ type: 'SET_MODEL_LOADING', payload: false });
      dispatch({ type: 'SET_MODEL_ERROR', payload: error.message });
    }
  };

  const handleUnloadModel = () => {
    dispatch({ type: 'UNLOAD_MODEL' });
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        title: 'Model Unloaded',
        message: 'Model has been unloaded from memory',
        type: 'info',
        timestamp: new Date().toLocaleTimeString(),
      }
    });
  };

  const refreshModels = () => {
    dispatch({ type: 'REFRESH_AVAILABLE_MODELS' });
  };

  const getBackendColor = (backend) => {
    switch (backend) {
      case 'CUDA': return 'success';
      case 'ROCm': return 'primary';
      case 'AWS GPU': return 'secondary';
      default: return 'default';
    }
  };

  const availableBackends = ['CPU', 'CUDA', 'ROCm'];
  if (state.systemInfo.awsDetected) {
    availableBackends.push('AWS GPU');
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Model Manager
      </Typography>

      <Grid container spacing={3}>
        {/* Current Model Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Current Model Status
              </Typography>

              {state.models.loaded ? (
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Typography variant="h6">{state.models.loaded.name}</Typography>
                    <Chip
                      label={state.models.loaded.backend}
                      color={getBackendColor(state.models.loaded.backend)}
                      size="small"
                    />
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Storage fontSize="small" />
                        <Typography variant="body2">
                          Size: {state.models.loaded.size} MB
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Speed fontSize="small" />
                        <Typography variant="body2">
                          Type: {state.models.loaded.type}
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>

                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                    Loaded: {new Date(state.models.loaded.loadedAt).toLocaleString()}
                  </Typography>

                  <Button
                    variant="outlined"
                    color="error"
                    onClick={handleUnloadModel}
                    sx={{ mt: 2 }}
                    fullWidth
                  >
                    Unload Model
                  </Button>
                </Box>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Memory sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Model Loaded
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Select and load a model to start inference
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Model Loading Controls */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">
                  Load Model
                </Typography>
                <Tooltip title="Refresh model list">
                  <IconButton onClick={refreshModels} size="small">
                    <Refresh />
                  </IconButton>
                </Tooltip>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Select Model</InputLabel>
                    <Select
                      value={selectedModel}
                      label="Select Model"
                      onChange={(e) => setSelectedModel(e.target.value)}
                    >
                      {state.models.available.map((model) => (
                        <MenuItem key={model} value={model}>
                          {model}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Backend</InputLabel>
                    <Select
                      value={selectedBackend}
                      label="Backend"
                      onChange={(e) => setSelectedBackend(e.target.value)}
                    >
                      {availableBackends.map((backend) => (
                        <MenuItem key={backend} value={backend}>
                          {backend}
                          {backend === 'CUDA' && state.systemInfo.gpus.length > 0 && (
                            <Chip
                              label={`${state.systemInfo.gpus.length} GPU${state.systemInfo.gpus.length > 1 ? 's' : ''}`}
                              size="small"
                              sx={{ ml: 1 }}
                            />
                          )}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={() => selectedModel ? handleLoadModel() : setLoadDialogOpen(true)}
                    disabled={state.models.loading}
                    startIcon={<CloudDownload />}
                  >
                    {state.models.loading ? 'Loading...' : 'Load Model'}
                  </Button>
                </Grid>

                <Grid item xs={12}>
                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={() => setLoadDialogOpen(true)}
                    startIcon={<Info />}
                  >
                    Load Custom Model
                  </Button>
                </Grid>
              </Grid>

              {state.models.loading && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                    Loading model... This may take a few minutes.
                  </Typography>
                </Box>
              )}

              {state.models.loadError && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {state.models.loadError}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* System Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Information
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Backend Detection
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Chip
                      label={`Current: ${state.systemInfo.backendType}`}
                      color="primary"
                      size="small"
                    />
                    {state.systemInfo.awsDetected && (
                      <Chip
                        label="AWS Instance Detected"
                        color="secondary"
                        size="small"
                      />
                    )}
                  </Box>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Available GPUs
                  </Typography>
                  {state.systemInfo.gpus.length > 0 ? (
                    <List dense>
                      {state.systemInfo.gpus.map((gpu, index) => (
                        <ListItem key={index} sx={{ pl: 0 }}>
                          <ListItemText
                            primary={`GPU ${index}: ${gpu.name}`}
                            secondary={`${gpu.memoryTotal}MB Total Memory`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No GPUs detected
                    </Typography>
                  )}
                </Grid>

                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Memory Usage
                  </Typography>
                  <Box>
                    <Typography variant="body2">
                      System: {state.systemInfo.memoryUsage}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={state.systemInfo.memoryUsage}
                      sx={{ mt: 1, height: 6, borderRadius: 3 }}
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Custom Model Dialog */}
      <Dialog open={loadDialogOpen} onClose={() => setLoadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Load Custom Model</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Model Name or Path"
            fullWidth
            variant="outlined"
            value={customModelName}
            onChange={(e) => setCustomModelName(e.target.value)}
            placeholder="e.g., microsoft/DialoGPT-medium"
            helperText="Enter a HuggingFace model name or local path"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLoadDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleLoadModel}
            variant="contained"
            disabled={!customModelName.trim()}
          >
            Load
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ModelManager;
