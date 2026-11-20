import { memo } from 'react';
import { Link, Outlet } from 'react-router-dom';
import { ApiStatus } from '@/feature/api-status/api-status';
import { CampaignCrumbs } from '@/feature/campaign-crumbs/campaign-crumbs';
import { Shell } from '@/ui';
import styles from './app-shell.module.css';

const side = (
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

const top = (
  <>
    <CampaignCrumbs />
    <ApiStatus />
  </>
);

const outlet = <Outlet />;

/** Sidebar, trail, and health around the current page. */
export const AppShell = memo(function AppShell() {
  return (
    <Shell side={side} top={top}>
      {outlet}
    </Shell>
  );
});
