"use client"

import { useState, useEffect } from 'react'

export default function Home() {
  const [products, setProducts] = useState([])
  const [users, setUsers] = useState([])

  useEffect(() => {
    // Fetch from API gateway
    const fetchData = async () => {
      const productsRes = await fetch('http://localhost:3001/api/products')
      const productsData = await productsRes.json()
      setProducts(productsData)

      const usersRes = await fetch('http://localhost:3001/api/users')
      const usersData = await usersRes.json()
      setUsers(usersData)
    }
    fetchData()
  }, [])

  return (
    <div>
      <h1>Microservices Demo</h1>
      
      <h2>Products</h2>
      <ul>
        {products.map(product => (
          <li key={product.id}>{product.name} - ${product.price}</li>
        ))}
      </ul>

      <h2>Users</h2>
      <ul>
        {users.map(user => (
          <li key={user.id}>{user.name} - {user.email}</li>
        ))}
      </ul>
    </div>
  )
}