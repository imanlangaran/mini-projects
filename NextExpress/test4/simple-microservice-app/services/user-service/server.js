// services/user-service/server.js
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3002;

// --- In-memory Data Store ---
const users = [
    { id: 101, name: 'Alice', email: 'alice@example.com' },
    { id: 102, name: 'Bob', email: 'bob@example.com' },
];
// ---------------------------

app.use(cors()); // Enable CORS
app.use(express.json());

// --- API Routes ---
app.get('/api/users', (req, res) => {
    console.log(`[User Service] GET /api/users requested`);
    res.json(users);
});

app.get('/api/users/:id', (req, res) => {
    const id = parseInt(req.params.id, 10);
    const user = users.find(u => u.id === id);
    console.log(`[User Service] GET /api/users/${id} requested`);
    if (user) {
        res.json(user);
    } else {
        res.status(404).json({ message: 'User not found' });
    }
});
// -----------------

app.listen(PORT, () => {
    console.log(`[User Service] Running on http://localhost:${PORT}`);
});