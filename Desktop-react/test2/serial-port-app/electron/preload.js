import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electron', {
  onSerialPortData: (callback) => ipcRenderer.on('serialport-data', callback),
});