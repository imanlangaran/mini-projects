import { StrictMode, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

const Main = () => {
  useEffect(() => {
    const script = document.createElement('script');
    script.type = 'module';
    script.src = '/src/js/main.js';
    document.body.appendChild(script);
  }, []);

  return (
    <StrictMode>
      <App />
    </StrictMode>
  );
};

createRoot(document.getElementById('root')).render(<Main />);