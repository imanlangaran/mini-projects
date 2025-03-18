import React, { useState, useEffect } from 'react';

function App() {
  const [data, setData] = useState('');
  const [portOpen, setPortOpen] = useState(false);

  useEffect(() => {
    if (window.electron) {
      window.electron.on('serial-data', (newData) => {
        setData((prevData) => prevData + newData);
      });
    }
  }, []);

  const handleOpenPort = () => {
    if (window.electron) {
      window.electron.send('open-port', { path: 'COM3', baudRate: 9600 });
      setPortOpen(true);
    }
  };

  const handleClosePort = () => {
    if (window.electron) {
      window.electron.send('close-port');
      setPortOpen(false);
    }
  };

  return (
    <div>
      <h1>Serial Port Data</h1>
      <pre>{data}</pre>
      {!portOpen ? (
        <button onClick={handleOpenPort}>Open Port</button>
      ) : (
        <button onClick={handleClosePort}>Close Port</button>
      )}
    </div>
  );
}

export default App;