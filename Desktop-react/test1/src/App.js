import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [status, setStatus] = useState('Not Connected');
  const [messages, setMessages] = useState([]);
  const [port, setPort] = useState('COM3'); // Change to your serial port
  const [baudRate, setBaudRate] = useState(9600);

  useEffect(() => {
    // Listen for serial data
    window.serial.onData((event, data) => {
      setMessages((prev) => [...prev, `Received: ${data}`]);
    });
  }, []);

  const toggleConnection = async () => {
    if (status === 'Not Connected') {
      const result = await window.serial.connect(port, baudRate);
      setStatus(result);
    } else {
      const result = await window.serial.disconnect();
      setStatus(result);
    }
  };

  return (
    <div className="App">
      <h1>Serial Port Reader</h1>
      <p>Status: {status}</p>
      <div>
        <input
          type="text"
          value={port}
          onChange={(e) => setPort(e.target.value)}
          placeholder="Enter serial port"
        />
        <input
          type="number"
          value={baudRate}
          onChange={(e) => setBaudRate(Number(e.target.value))}
          placeholder="Enter baud rate"
        />
        <button onClick={toggleConnection}>
          {status === 'Not Connected' ? 'Connect' : 'Disconnect'}
        </button>
      </div>
      <div className="messages">
        {messages.map((msg, index) => (
          <p key={index}>{msg}</p>
        ))}
      </div>
    </div>
  );
}

export default App;
