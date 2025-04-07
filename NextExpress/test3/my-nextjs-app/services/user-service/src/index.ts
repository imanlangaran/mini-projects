import express from 'express';
import { User, UserResponse } from './types';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

app.get('/users', (req, res) => {
    // Logic to fetch users
    const users: UserResponse = {
        users: [], // Replace with actual user fetching logic
    };
    res.json(users);
});

app.post('/users', (req, res) => {
    const newUser: User = req.body;
    // Logic to create a new user
    res.status(201).json(newUser);
});

app.listen(PORT, () => {
    console.log(`User service is running on port ${PORT}`);
});