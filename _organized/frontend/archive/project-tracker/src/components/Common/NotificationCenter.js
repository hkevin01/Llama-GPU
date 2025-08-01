import { formatDistanceToNow } from 'date-fns';
import { AlertCircle, AlertTriangle, CheckCircle, Info, X } from 'lucide-react';
import { useEffect } from 'react';
import { useProject } from '../../context/ProjectContext';
import './NotificationCenter.css';

function NotificationCenter() {
  const { state, dispatch } = useProject();
  const { notifications } = state.ui;
  const { notifications: notificationList } = state;

  const handleClose = () => {
    dispatch({ type: 'TOGGLE_NOTIFICATIONS' });
  };

  const markAsRead = (id) => {
    dispatch({
      type: 'MARK_NOTIFICATION_READ',
      payload: { id }
    });
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="notification-icon success" size={20} />;
      case 'warning':
        return <AlertTriangle className="notification-icon warning" size={20} />;
      case 'error':
        return <AlertCircle className="notification-icon error" size={20} />;
      default:
        return <Info className="notification-icon info" size={20} />;
    }
  };

  // Auto-close after 5 seconds if no unread notifications
  useEffect(() => {
    const unreadCount = notificationList.filter(n => !n.read).length;
    if (notifications.isOpen && unreadCount === 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [notifications.isOpen, notificationList]);

  if (!notifications.isOpen) {
    return null;
  }

  return (
    <div className="notification-overlay" onClick={handleClose}>
      <div className="notification-panel" onClick={e => e.stopPropagation()}>
        <div className="notification-header">
          <h3>Notifications</h3>
          <button className="close-button" onClick={handleClose}>
            <X size={20} />
          </button>
        </div>

        <div className="notification-list">
          {notificationList.length === 0 ? (
            <div className="empty-notifications">
              <Info size={32} className="empty-icon" />
              <p>No notifications yet</p>
              <span>You'll see project updates here</span>
            </div>
          ) : (
            notificationList.map((notification) => (
              <div
                key={notification.id}
                className={`notification-item ${notification.read ? 'read' : 'unread'}`}
                onClick={() => markAsRead(notification.id)}
              >
                {getNotificationIcon(notification.type)}
                <div className="notification-content">
                  <h4>{notification.title}</h4>
                  <p>{notification.message}</p>
                  <span className="notification-time">
                    {formatDistanceToNow(notification.timestamp, { addSuffix: true })}
                  </span>
                </div>
                {!notification.read && <div className="unread-indicator" />}
              </div>
            ))
          )}
        </div>

        {notificationList.length > 0 && (
          <div className="notification-footer">
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => {
                notificationList.forEach(n => {
                  if (!n.read) markAsRead(n.id);
                });
              }}
            >
              Mark all as read
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default NotificationCenter;
