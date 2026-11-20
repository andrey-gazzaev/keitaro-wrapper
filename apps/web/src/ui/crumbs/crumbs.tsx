import { memo } from 'react';
import { Link } from 'react-router-dom';
import styles from './crumbs.module.css';

/** One segment of the trail above the page. */
export type Crumb = {
  /** Visible segment. */
  readonly label: string;

  /** Route for this segment. Absent on the current segment. */
  readonly href?: string;
};

type CrumbsProps = {
  /** Segments from the root to the current page. */
  readonly items: readonly Crumb[];
};

/** Trail of links. The last segment is the current page. */
export const Crumbs = memo(function Crumbs({ items }: CrumbsProps) {
  return (
    <nav className={styles.crumbs}>
      {items.map((item, index) => {
        const href = item.href;
        const linked = href !== undefined && index !== items.length - 1;

        return (
          <span key={`${item.label}-${index}`} className={styles.item}>
            {index > 0 ? <span aria-hidden="true">/</span> : null}
            {linked ? <Link to={href}>{item.label}</Link> : <span className={styles.current}>{item.label}</span>}
          </span>
        );
      })}
    </nav>
  );
});
