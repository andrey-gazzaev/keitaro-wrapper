import { memo } from 'react';
import { Link } from 'react-router-dom';
import styles from './app-shell-side.module.css';

/** Brand and the campaigns link. */
export const AppShellSide = memo(function AppShellSide() {
  return (
    <>
      <div className={styles.brand}>
        <span className={styles.mark}>K</span>
        <div>
          <strong>Keitaro</strong>
          <small>Обёртка над трекером</small>
        </div>
      </div>
      <Link className={styles.current} to="/">
        Кампании
      </Link>
    </>
  );
});
