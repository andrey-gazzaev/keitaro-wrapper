import { memo, type ReactNode } from 'react';
import styles from './page.module.css';

type PageProps = {
  /** Content of the page column. */
  readonly children: ReactNode;
};

/** Padded column for one page. */
export const Page = memo(function Page({ children }: PageProps) {
  return <main className={styles.page}>{children}</main>;
});
