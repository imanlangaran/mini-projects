import express from 'express';
import { AuthRequest, AuthResponse } from './types';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.post('/auth/login', (req: AuthRequest, res: AuthResponse) => {
    // Handle login logic here
    res.send({ message: 'Login successful' });
});

app.post('/auth/register', (req: AuthRequest, res: AuthResponse) => {
    // Handle registration logic here
    res.send({ message: 'Registration successful' });
});

app.listen(PORT, () => {
    console.log(`Auth service running on port ${PORT}`);
});