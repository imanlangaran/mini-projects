const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { SerialPort } = require('serialport');

let mainWindow;
let serialPort;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      enableRemoteModule: false,
    },
  });

  mainWindow.loadURL(
    process.env.NODE_ENV === 'development'
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../build/index.html')}`
  );

  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
}

// Handle serial port connection
ipcMain.handle('serial:connect', async (event, port, baudRate) => {
  try {
    serialPort = new SerialPort({ path: port, baudRate: baudRate });
    serialPort.on('data', (data) => {
      mainWindow.webContents.send('serial:data', data.toString());
    });
    return 'Connected';
  } catch (error) {
    return `Error: ${error.message}`;
  }
});

// Handle serial port disconnection
ipcMain.handle('serial:disconnect', () => {
  if (serialPort && serialPort.isOpen) {
    serialPort.close();
    return 'Disconnected';
  }
  return 'Not connected';
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});