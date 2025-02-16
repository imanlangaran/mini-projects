import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

const Main = () => {
  const [scriptLoaded, setScriptLoaded] = useState(false);

  useEffect(() => {
    const script = document.createElement('script');
    script.type = 'module';
    script.src = '/src/js/main.js';
    script.onload = () => setScriptLoaded(true);
    document.body.appendChild(script);
  }, []);

  if (!scriptLoaded) {
    return <div></div>;
  }

  return (
    <StrictMode>
      <App />
    </StrictMode>
  );
};

createRoot(document.getElementById('root')).render(<Main />);