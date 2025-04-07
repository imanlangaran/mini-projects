// frontend/pages/index.js
import Head from 'next/head';
import styles from '../styles/Home.module.css';

// This function runs on the server for every request
export async function getServerSideProps(context) {
  let products = [];
  let users = [];
  let productError = null;
  let userError = null;

  // Fetch data from product service
  try {
    const productRes = await fetch(`${process.env.NEXT_PUBLIC_PRODUCT_SERVICE_URL}/api/products`);
    if (!productRes.ok) {
        throw new Error(`Failed to fetch products: ${productRes.statusText}`);
    }
    products = await productRes.json();
  } catch (error) {
    console.error("Error fetching products:", error);
    productError = error.message || 'Could not load products.';
  }

  // Fetch data from user service
  try {
    const userRes = await fetch(`${process.env.NEXT_PUBLIC_USER_SERVICE_URL}/api/users`);
     if (!userRes.ok) {
        throw new Error(`Failed to fetch users: ${userRes.statusText}`);
    }
    users = await userRes.json();
  } catch (error) {
    console.error("Error fetching users:", error);
    userError = error.message || 'Could not load users.';
  }

  // Pass data to the page via props
  return {
    props: {
      products,
      users,
      productError,
      userError,
    },
  };
}

export default function Home({ products, users, productError, userError }) {
  return (
    <div className={styles.container}>
      <Head>
        <title>Microservice Demo App</title>
        <meta name="description" content="Next.js frontend with microservices" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>
          Welcome to the Microservice Demo!
        </h1>

        <section className={styles.grid}>
          <div className={styles.card}>
            <h2>Products</h2>
            {productError ? (
                <p style={{ color: 'red' }}>Error: {productError}</p>
            ) : products.length > 0 ? (
                <ul>
                    {products.map((product) => (
                    <li key={product.id}>
                        {product.name} - ${product.price}
                    </li>
                    ))}
                </ul>
            ) : (
                <p>No products found.</p>
            )}
          </div>

          <div className={styles.card}>
            <h2>Users</h2>
             {userError ? (
                <p style={{ color: 'red' }}>Error: {userError}</p>
            ) : users.length > 0 ? (
                <ul>
                    {users.map((user) => (
                    <li key={user.id}>
                        {user.name} ({user.email})
                    </li>
                    ))}
                </ul>
             ) : (
                <p>No users found.</p>
             )}
          </div>
        </section>
      </main>
    </div>
  );
}