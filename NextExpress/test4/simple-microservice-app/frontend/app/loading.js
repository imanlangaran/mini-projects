// frontend/app/loading.js
import { Skeleton } from "@radix-ui/themes"; // Import Skeleton
import styles from '../styles/Home.module.css';

export default function Loading() {
  // Define some base styles for the skeletons for consistency
  const skeletonBaseStyle = {
    backgroundColor: '#e2e8f0', // A light gray color (Tailwind's gray-200)
    borderRadius: '4px',        // Slightly rounded corners
  };

  const skeletonItemStyle = {
    ...skeletonBaseStyle,
    height: '20px',           // Height for list-like items
    marginBottom: '0.75rem',  // Space below each item
  };

  return (
    <div className={styles.container}>
      <main className={styles.main}>
        {/* Skeleton for the main title */}
        <Skeleton style={{
          ...skeletonBaseStyle,
          height: '40px',       // Approx height of the h1
          width: '60%',         // Approx width
          marginBottom: '2.5rem' // Match spacing below title
        }} />

        <section className={styles.grid}>
          {/* Skeleton for Products Card */}
          <div className={styles.card}>
            {/* Skeleton for card title (h2) */}
            <Skeleton style={{
              ...skeletonBaseStyle,
              height: '32px',     // Approx height of the h2
              width: '120px',     // Approx width of "Products"
              marginBottom: '1.5rem' // Match spacing below h2
            }} />
            {/* Skeletons for product list items */}
            <div>
              <Skeleton style={{ ...skeletonItemStyle, width: '85%' }} />
              <Skeleton style={{ ...skeletonItemStyle, width: '70%' }} />
              <Skeleton style={{ ...skeletonItemStyle, width: '75%' }} />
            </div>
          </div>

          {/* Skeleton for Users Card */}
          <div className={styles.card}>
            {/* Skeleton for card title (h2) */}
            <Skeleton style={{
              ...skeletonBaseStyle,
              height: '32px',
              width: '90px',     // Approx width of "Users"
              marginBottom: '1.5rem'
            }} />
            {/* Skeletons for user list items */}
            <div>
              <Skeleton style={{ ...skeletonItemStyle, width: '90%' }} />
              <Skeleton style={{ ...skeletonItemStyle, width: '80%' }} />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}