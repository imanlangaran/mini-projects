const { SerialPort } = require('serialport');

let port;

const openPort = (path, baudRate) => {
  port = new SerialPort({ path, baudRate }, (err) => {
    if (err) {
      console.error('Error opening port:', err.message);
    } else {
      console.log('Serial port opened');
    }
  });

  port.on('data', (data) => {
    const dataString = data.toString();
    console.log('Data:', dataString);
    // Send data to the renderer process
    if (window.electron) {
      window.electron.send('serial-data', dataString);
    }
  });

  port.on('error', (err) => {
    console.error('Error:', err.message);
  });
};

const closePort = () => {
  if (port) {
    port.close((err) => {
      if (err) {
        console.error('Error closing port:', err.message);
      } else {
        console.log('Serial port closed');
      }
    });
  }
};

module.exports = { openPort, closePort };