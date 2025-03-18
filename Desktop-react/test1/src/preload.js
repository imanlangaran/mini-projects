const { contextBridge, ipcRenderer } = require('electron');

// Expose serial port functions to the renderer process
contextBridge.exposeInMainWorld('serial', {
  connect: (port, baudRate) => ipcRenderer.invoke('serial:connect', port, baudRate),
  disconnect: () => ipcRenderer.invoke('serial:disconnect'),
  onData: (callback) => ipcRenderer.on('serial:data', callback),
});