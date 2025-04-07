// frontend/app/page.js
import styles from '../styles/Home.module.css'; // Reuse the styles

// Helper function to fetch data and handle basic errors
async function fetchData(url, serviceName) {
  await new Promise(resolve => setTimeout(resolve, 1500)); // Add 1.5 second delay
  try {
    // App Router's fetch is automatically cached.
    // Use { cache: 'no-store' } to mimic getServerSideProps behavior (fetch on every request).
    // Omit it if you want caching (data might be stale between requests/deploys).
    const res = await fetch(url, { cache: 'no-store' });

    if (!res.ok) {
      // Provide more context in the error
      throw new Error(`Failed to fetch ${serviceName}: ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    return { data, error: null };
  } catch (error) {
    console.error(`Error fetching ${serviceName}:`, error);
    // Return a structured error
    return { data: [], error: error.message || `Could not load ${serviceName}.` };
  }
}

// This is an async Server Component
export default async function HomePage() {
  // Fetch data directly within the Server Component
  const productUrl = `${process.env.NEXT_PUBLIC_PRODUCT_SERVICE_URL}/api/products`;
  const userUrl = `${process.env.NEXT_PUBLIC_USER_SERVICE_URL}/api/users`;

  // Fetch in parallel for efficiency
  const [productResult, userResult] = await Promise.all([
    fetchData(productUrl, 'products'),
    fetchData(userUrl, 'users')
  ]);

  const { data: products, error: productError } = productResult;
  const { data: users, error: userError } = userResult;

  // Render the JSX
  return (
    <div className={styles.container}>
       {/* Note: Head component is replaced by Metadata API in layout.js */}
      <main className={styles.main}>
        <h1 className={styles.title}>
          Welcome to the Microservice Demo! (App Router)
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