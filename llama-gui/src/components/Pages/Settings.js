import {
    Download,
    Palette,
    RestoreFromTrash,
    Save,
    Speed,
    Upload
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
    ListItemSecondaryAction,
    ListItemText,
    MenuItem,
    Select,
    Switch,
    TextField,
    Typography,
} from '@mui/material';
import { useState } from 'react';
import { useAppContext } from '../../context/AppContext';

function Settings() {
  const { state, dispatch } = useAppContext();
  const [settings, setSettings] = useState({
    darkMode: state.ui.darkMode,
    language: 'en',
    autoRefresh: true,
    refreshInterval: 30,
    enableNotifications: true,
    enableSounds: false,
    maxLogEntries: 1000,
    defaultBackend: 'CPU',
    autoLoadModel: false,
    saveMetrics: true,
    compressionLevel: 'medium',
    debugMode: false,
  });

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const saveSettings = () => {
    // Apply theme change immediately
    if (settings.darkMode !== state.ui.darkMode) {
      dispatch({ type: 'TOGGLE_THEME' });
    }

    dispatch({
      type: 'UPDATE_SETTINGS',
      payload: settings
    });

    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        title: 'Settings Saved',
        message: 'Your preferences have been saved successfully',
        type: 'success',
        timestamp: new Date().toLocaleTimeString(),
      }
    });
  };

  const resetToDefaults = () => {
    const defaultSettings = {
      darkMode: false,
      language: 'en',
      autoRefresh: true,
      refreshInterval: 30,
      enableNotifications: true,
      enableSounds: false,
      maxLogEntries: 1000,
      defaultBackend: 'CPU',
      autoLoadModel: false,
      saveMetrics: true,
      compressionLevel: 'medium',
      debugMode: false,
    };

    setSettings(defaultSettings);
    dispatch({
      type: 'ADD_NOTIFICATION',
      payload: {
        title: 'Settings Reset',
        message: 'Settings have been reset to defaults',
        type: 'info',
        timestamp: new Date().toLocaleTimeString(),
      }
    });
  };

  const exportSettings = () => {
    const configData = {
      settings,
      systemInfo: state.systemInfo,
      multiGPU: state.multiGPU,
      quantization: state.quantization,
      exportDate: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(configData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `llama-gpu-config-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const importSettings = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const config = JSON.parse(e.target.result);
            if (config.settings) {
              setSettings(config.settings);
              dispatch({
                type: 'ADD_NOTIFICATION',
                payload: {
                  title: 'Settings Imported',
                  message: 'Configuration has been imported successfully',
                  type: 'success',
                  timestamp: new Date().toLocaleTimeString(),
                }
              });
            }
          } catch (error) {
            dispatch({
              type: 'ADD_NOTIFICATION',
              payload: {
                title: 'Import Failed',
                message: 'Invalid configuration file',
                type: 'error',
                timestamp: new Date().toLocaleTimeString(),
              }
            });
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Settings
      </Typography>

      <Grid container spacing={3}>
        {/* Appearance Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Palette sx={{ mr: 1, verticalAlign: 'middle' }} />
                Appearance
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.darkMode}
                    onChange={(e) => handleSettingChange('darkMode', e.target.checked)}
                  />
                }
                label="Dark Mode"
                sx={{ display: 'block', mb: 2 }}
              />

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Language</InputLabel>
                <Select
                  value={settings.language}
                  label="Language"
                  onChange={(e) => handleSettingChange('language', e.target.value)}
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="es">Español</MenuItem>
                  <MenuItem value="fr">Français</MenuItem>
                  <MenuItem value="de">Deutsch</MenuItem>
                  <MenuItem value="zh">中文</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoRefresh}
                    onChange={(e) => handleSettingChange('autoRefresh', e.target.checked)}
                  />
                }
                label="Auto Refresh Data"
                sx={{ display: 'block', mb: 2 }}
              />

              {settings.autoRefresh && (
                <TextField
                  fullWidth
                  label="Refresh Interval (seconds)"
                  type="number"
                  value={settings.refreshInterval}
                  onChange={(e) => handleSettingChange('refreshInterval', parseInt(e.target.value))}
                  inputProps={{ min: 5, max: 300 }}
                />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Notification Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notifications
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableNotifications}
                    onChange={(e) => handleSettingChange('enableNotifications', e.target.checked)}
                  />
                }
                label="Enable Notifications"
                sx={{ display: 'block', mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableSounds}
                    onChange={(e) => handleSettingChange('enableSounds', e.target.checked)}
                    disabled={!settings.enableNotifications}
                  />
                }
                label="Sound Alerts"
                sx={{ display: 'block', mb: 2 }}
              />

              <TextField
                fullWidth
                label="Max Log Entries"
                type="number"
                value={settings.maxLogEntries}
                onChange={(e) => handleSettingChange('maxLogEntries', parseInt(e.target.value))}
                inputProps={{ min: 100, max: 10000 }}
                helperText="Maximum number of log entries to keep in memory"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Speed sx={{ mr: 1, verticalAlign: 'middle' }} />
                Performance
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Default Backend</InputLabel>
                <Select
                  value={settings.defaultBackend}
                  label="Default Backend"
                  onChange={(e) => handleSettingChange('defaultBackend', e.target.value)}
                >
                  <MenuItem value="CPU">CPU</MenuItem>
                  <MenuItem value="CUDA">CUDA</MenuItem>
                  <MenuItem value="ROCm">ROCm</MenuItem>
                  <MenuItem value="AWS GPU">AWS GPU</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoLoadModel}
                    onChange={(e) => handleSettingChange('autoLoadModel', e.target.checked)}
                  />
                }
                label="Auto-load Last Model"
                sx={{ display: 'block', mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.saveMetrics}
                    onChange={(e) => handleSettingChange('saveMetrics', e.target.checked)}
                  />
                }
                label="Save Performance Metrics"
                sx={{ display: 'block', mb: 2 }}
              />

              <FormControl fullWidth>
                <InputLabel>Data Compression</InputLabel>
                <Select
                  value={settings.compressionLevel}
                  label="Data Compression"
                  onChange={(e) => handleSettingChange('compressionLevel', e.target.value)}
                >
                  <MenuItem value="low">Low (Better Performance)</MenuItem>
                  <MenuItem value="medium">Medium (Balanced)</MenuItem>
                  <MenuItem value="high">High (Better Storage)</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Advanced Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Advanced
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.debugMode}
                    onChange={(e) => handleSettingChange('debugMode', e.target.checked)}
                  />
                }
                label="Debug Mode"
                sx={{ display: 'block', mb: 2 }}
              />

              {settings.debugMode && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  Debug mode will increase log verbosity and may impact performance.
                </Alert>
              )}

              <Typography variant="subtitle2" gutterBottom>
                System Information
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText
                    primary="GPUs Detected"
                    secondary={`${state.systemInfo.gpus.length} GPU${state.systemInfo.gpus.length !== 1 ? 's' : ''}`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Backend"
                    secondary={state.systemInfo.backendType}
                  />
                  <ListItemSecondaryAction>
                    <Chip
                      label={state.systemInfo.awsDetected ? 'AWS' : 'Local'}
                      size="small"
                      color={state.systemInfo.awsDetected ? 'secondary' : 'default'}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="API Server"
                    secondary={state.systemInfo.apiServerStatus}
                  />
                  <ListItemSecondaryAction>
                    <Chip
                      label={state.systemInfo.apiServerStatus === 'connected' ? 'Online' : 'Offline'}
                      size="small"
                      color={state.systemInfo.apiServerStatus === 'connected' ? 'success' : 'default'}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Configuration Management
              </Typography>

              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  startIcon={<Save />}
                  onClick={saveSettings}
                >
                  Save Settings
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<RestoreFromTrash />}
                  onClick={resetToDefaults}
                >
                  Reset to Defaults
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<Download />}
                  onClick={exportSettings}
                >
                  Export Config
                </Button>

                <Button
                  variant="outlined"
                  startIcon={<Upload />}
                  onClick={importSettings}
                >
                  Import Config
                </Button>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="body2" color="text.secondary">
                Configuration includes all settings, GPU configuration, quantization preferences,
                and system optimizations. Exported configurations can be shared across different
                installations or used as backups.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Settings;
