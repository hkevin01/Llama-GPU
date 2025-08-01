import { Alert, Slide, Snackbar } from '@mui/material';
import { useEffect, useState } from 'react';
import { useAppContext } from '../../context/AppContext';

function SlideTransition(props) {
  return <Slide {...props} direction="left" />;
}

function NotificationSystem() {
  const { state, dispatch } = useAppContext();
  const [open, setOpen] = useState(false);
  const [currentNotification, setCurrentNotification] = useState(null);

  useEffect(() => {
    if (state.notifications.items.length > 0 && !open) {
      const unreadNotifications = state.notifications.items.filter(n => !n.read);
      if (unreadNotifications.length > 0) {
        setCurrentNotification(unreadNotifications[0]);
        setOpen(true);
      }
    }
  }, [state.notifications.items, open]);

  const handleClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);

    // Mark as read
    if (currentNotification) {
      dispatch({
        type: 'MARK_NOTIFICATION_READ',
        payload: currentNotification.id
      });
    }
  };

  const handleExited = () => {
    setCurrentNotification(null);
  };

  if (!currentNotification) {
    return null;
  }

  const getSeverity = (type) => {
    switch (type) {
      case 'success': return 'success';
      case 'error': return 'error';
      case 'warning': return 'warning';
      default: return 'info';
    }
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={4000}
      onClose={handleClose}
      TransitionComponent={SlideTransition}
      onExited={handleExited}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
    >
      <Alert
        onClose={handleClose}
        severity={getSeverity(currentNotification.type)}
        variant="filled"
        sx={{ width: '100%' }}
      >
        <strong>{currentNotification.title}</strong>
        {currentNotification.message && (
          <>
            <br />
            {currentNotification.message}
          </>
        )}
      </Alert>
    </Snackbar>
  );
}

export default NotificationSystem;
