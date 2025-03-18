import React, { useEffect, useState } from 'react';

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    window.electron.onSerialPortData((event, data) => {
      setMessage(data);
    });
  }, []);

  return (
    <div>
      <h1>Serial Port Data</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;