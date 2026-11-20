import { memo, type ReactNode } from 'react';
import styles from './page-head.module.css';

type PageHeadProps = {
  /** Page title. */
  readonly title: string;

  /** Sentence under the title. Absent when the page has none. */
  readonly description?: string;

  /** Controls at the end of the heading. Absent when the page has none. */
  readonly actions?: ReactNode;
};

/** Title, description, and the page's actions. */
export const PageHead = memo(function PageHead({ title, description, actions }: PageHeadProps) {
  return (
    <header className={styles.head}>
      <div className={styles.copy}>
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
      </div>
      {actions ? <div className={styles.actions}>{actions}</div> : null}
    </header>
  );
});
