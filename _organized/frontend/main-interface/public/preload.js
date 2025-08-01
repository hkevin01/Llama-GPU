const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),

  // API communication
  apiRequest: (method, endpoint, data) =>
    ipcRenderer.invoke('api-request', { method, endpoint, data }),

  // Menu events
  onNewSession: (callback) => ipcRenderer.on('new-session', callback),
  onOpenSettings: (callback) => ipcRenderer.on('open-settings', callback),
  onShowAbout: (callback) => ipcRenderer.on('show-about', callback),

  // Cleanup
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});
