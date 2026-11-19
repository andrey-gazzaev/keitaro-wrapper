import type { ReactNode } from 'react';
import styles from './page.module.css';

type PageProps = {
  /** Content of the page column. */
  readonly children: ReactNode;
};

/** Centered column for one page. */
export function Page({ children }: PageProps) {
  return <main className={styles.page}>{children}</main>;
}
