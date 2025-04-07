import express from 'express';
import bodyParser from 'body-parser';
import { User, AuthResponse } from './types';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(bodyParser.json());

app.post('/auth/login', (req, res) => {
    const { username, password } = req.body;
    // Authentication logic here
    const user: User = { username }; // Example user object
    const response: AuthResponse = { token: 'example-token', user };
    res.json(response);
});

app.post('/auth/register', (req, res) => {
    const { username, password } = req.body;
    // Registration logic here
    const user: User = { username }; // Example user object
    const response: AuthResponse = { token: 'example-token', user };
    res.status(201).json(response);
});

app.listen(PORT, () => {
    console.log(`Authentication service running on port ${PORT}`);
});