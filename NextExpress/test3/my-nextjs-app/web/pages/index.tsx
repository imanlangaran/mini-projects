import { useEffect, useState } from 'react';

const Home = () => {
  const [userData, setUserData] = useState(null);
  const [authData, setAuthData] = useState(null);

  useEffect(() => {
    const fetchUserData = async () => {
      const response = await fetch('/api/users');
      const data = await response.json();
      setUserData(data);
    };

    const fetchAuthData = async () => {
      const response = await fetch('/api/auth');
      const data = await response.json();
      setAuthData(data);
    };

    fetchUserData();
    fetchAuthData();
  }, []);

  return (
    <div>
      <h1>Welcome to My Next.js App</h1>
      <h2>User Data</h2>
      {userData ? (
        <pre>{JSON.stringify(userData, null, 2)}</pre>
      ) : (
        <p>Loading user data...</p>
      )}
      <h2>Authentication Data</h2>
      {authData ? (
        <pre>{JSON.stringify(authData, null, 2)}</pre>
      ) : (
        <p>Loading authentication data...</p>
      )}
    </div>
  );
};

export default Home;