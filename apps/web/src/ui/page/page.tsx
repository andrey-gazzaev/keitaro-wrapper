import type { ReactNode } from 'react';
import styles from './page.module.css';

/** Centered column for one page. */
export function Page({ children }: { readonly children: ReactNode }) {
  return <main className={styles.page}>{children}</main>;
}
