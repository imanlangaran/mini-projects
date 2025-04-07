// services/product-service/server.js
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3001;

// --- In-memory Data Store ---
const products = [
    { id: 1, name: 'Laptop Pro', price: 1200 },
    { id: 2, name: 'Wireless Mouse', price: 25 },
    { id: 3, name: 'Mechanical Keyboard', price: 75 },
];
// ---------------------------

app.use(cors()); // Enable CORS for all origins (adjust for production)
app.use(express.json()); // Parse JSON bodies

// --- API Routes ---
app.get('/api/products', (req, res) => {
    console.log(`[Product Service] GET /api/products requested`);
    res.json(products);
});

app.get('/api/products/:id', (req, res) => {
    const id = parseInt(req.params.id, 10);
    const product = products.find(p => p.id === id);
    console.log(`[Product Service] GET /api/products/${id} requested`);
    if (product) {
        res.json(product);
    } else {
        res.status(404).json({ message: 'Product not found' });
    }
});
// -----------------

app.listen(PORT, () => {
    console.log(`[Product Service] Running on http://localhost:${PORT}`);
});