import express from 'express';
import { UserRequest, UserResponse } from './types';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

app.get('/users', (req: UserRequest, res: UserResponse) => {
    // Logic to retrieve users
    res.send('List of users');
});

app.post('/users', (req: UserRequest, res: UserResponse) => {
    // Logic to create a new user
    res.send('User created');
});

app.listen(PORT, () => {
    console.log(`User service is running on port ${PORT}`);
});