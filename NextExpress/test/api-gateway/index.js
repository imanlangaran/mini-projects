const express = require('express')
const { createProxyMiddleware } = require('http-proxy-middleware')
const cors = require('cors')

const app = express()
app.use(cors())

// Products service proxy
app.use('/api/products', createProxyMiddleware({
  target: 'http://products-service:3002',
  changeOrigin: true,
  pathRewrite: { '^/api/products': '' }
}))

// Users service proxy
app.use('/api/users', createProxyMiddleware({
  target: 'http://users-service:3003',
  changeOrigin: true,
  pathRewrite: { '^/api/users': '' }
}))

app.listen(3001, () => {
  console.log('API Gateway running on port 3001')
})