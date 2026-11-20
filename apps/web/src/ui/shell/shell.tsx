import { memo, type ReactNode } from 'react';
import styles from './shell.module.css';

type ShellProps = {
  /** Sidebar content. */
  readonly side: ReactNode;

  /** Top bar content. */
  readonly top: ReactNode;

  /** Page body under the top bar. */
  readonly children: ReactNode;
};

/** Application frame: sidebar, top bar, and the page column. */
export const Shell = memo(function Shell({ side, top, children }: ShellProps) {
  return (
    <div className={styles.shell}>
      <aside className={styles.side}>{side}</aside>

      <div className={styles.main}>
        <header className={styles.top}>{top}</header>
        {children}
      </div>
    </div>
  );
});
