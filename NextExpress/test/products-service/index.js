const express = require('express')
const app = express()

const products = [
  { id: 1, name: 'Laptop', price: 999 },
  { id: 2, name: 'Phone', price: 699 },
  { id: 3, name: 'Tablet', price: 499 }
]

app.get('/', (req, res) => {
  res.json(products)
})

app.listen(3002, () => {
  console.log('Products service running on port 3002')
})