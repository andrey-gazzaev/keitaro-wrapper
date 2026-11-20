import { memo } from 'react';
import { mapApiStatus } from '@/mappers';
import { useHealth } from '@/queries';
import styles from './api-status.module.css';

/** Health of the API, shown in the top bar. */
export const ApiStatus = memo(function ApiStatus() {
  const health = useHealth();

  const status = health.data ? mapApiStatus(health.data) : null;

  if (health.isLoading) {
    return (
      <p className={`${styles.pill} ${styles.loading}`}>
        <i className={styles.dot} />
        Проверяем API…
      </p>
    );
  }

  if (health.isError || status == null) {
    return (
      <p className={`${styles.pill} ${styles.down}`}>
        <i className={styles.dot} />
        API не отвечает.
      </p>
    );
  }

  return (
    <p className={`${styles.pill} ${styles.ready}`}>
      <i className={styles.dot} />
      {status.label}
    </p>
  );
});
