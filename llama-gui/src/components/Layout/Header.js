import {
    AccountCircle,
    DarkMode,
    LightMode,
    Notifications,
    PowerSettingsNew,
    Settings,
} from '@mui/icons-material';
import {
    AppBar,
    Avatar,
    Badge,
    Box,
    FormControlLabel,
    IconButton,
    Menu,
    MenuItem,
    Switch,
    Toolbar,
    Tooltip,
    Typography,
} from '@mui/material';
import { useState } from 'react';
import { useAppContext } from '../../context/AppContext';

function Header() {
  const { state, dispatch } = useAppContext();
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState(null);

  const handleProfileMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleNotifications = (event) => {
    setNotificationsAnchor(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setNotificationsAnchor(null);
  };

  const toggleTheme = () => {
    dispatch({ type: 'TOGGLE_THEME' });
  };

  const getServerStatusColor = () => {
    switch (state.systemInfo?.apiServerStatus) {
      case 'connected': return 'success';
      case 'connecting': return 'warning';
      case 'error': return 'error';
      default: return 'info';
    }
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
      }}
    >
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
          🦙 Llama-GPU Interface
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* API Server Status */}
          <Tooltip title={`API Server: ${state.systemInfo.apiServerStatus}`}>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: (theme) => theme.palette?.[getServerStatusColor()]?.main || theme.palette.info.main,
                animation: state.systemInfo.apiServerStatus === 'connecting' ? 'pulse 1.5s infinite' : 'none',
              }}
            />
          </Tooltip>

          {/* Backend Type */}
          <Typography variant="body2" sx={{ px: 1 }}>
            {state.systemInfo.backendType}
            {state.systemInfo.awsDetected && ' (AWS)'}
          </Typography>

          {/* Theme Toggle */}
          <FormControlLabel
            control={
              <Switch
                checked={state.ui.darkMode}
                onChange={toggleTheme}
                icon={<LightMode />}
                checkedIcon={<DarkMode />}
              />
            }
            label=""
          />

          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton color="inherit" onClick={handleNotifications}>
              <Badge badgeContent={state.notifications.unread} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* Settings */}
          <Tooltip title="Settings">
            <IconButton color="inherit" onClick={() => dispatch({ type: 'SET_ACTIVE_PAGE', payload: 'settings' })}>
              <Settings />
            </IconButton>
          </Tooltip>

          {/* Profile Menu */}
          <Tooltip title="Account">
            <IconButton color="inherit" onClick={handleProfileMenu}>
              <Avatar sx={{ width: 32, height: 32 }}>
                <AccountCircle />
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>

        {/* Profile Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <MenuItem onClick={handleClose}>
            <AccountCircle sx={{ mr: 1 }} />
            Profile
          </MenuItem>
          <MenuItem onClick={handleClose}>
            <Settings sx={{ mr: 1 }} />
            Preferences
          </MenuItem>
          <MenuItem onClick={handleClose}>
            <PowerSettingsNew sx={{ mr: 1 }} />
            Sign Out
          </MenuItem>
        </Menu>

        {/* Notifications Menu */}
        <Menu
          anchorEl={notificationsAnchor}
          open={Boolean(notificationsAnchor)}
          onClose={handleClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          transformOrigin={{ vertical: 'top', horizontal: 'right' }}
          PaperProps={{ sx: { width: 320, maxHeight: 400 } }}
        >
          {state.notifications.items.length === 0 ? (
            <MenuItem>
              <Typography variant="body2" color="text.secondary">
                No notifications
              </Typography>
            </MenuItem>
          ) : (
            state.notifications.items.slice(0, 5).map((notification, index) => (
              <MenuItem key={index} onClick={handleClose}>
                <Box>
                  <Typography variant="body2" fontWeight={notification.read ? 400 : 600}>
                    {notification.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {notification.timestamp}
                  </Typography>
                </Box>
              </MenuItem>
            ))
          )}
        </Menu>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
