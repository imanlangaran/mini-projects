const express = require('express')
const app = express()

const users = [
  { id: 1, name: 'John Doe', email: 'john@example.com' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
]

app.get('/', (req, res) => {
  res.json(users)
})

app.listen(3003, () => {
  console.log('Users service running on port 3003')
})