import { memo, type ReactNode } from 'react';
import styles from './table-row.module.css';

type TableRowProps = {
  /** Plain has no fill. Draft is the yellow row. Removed is the gray row. */
  readonly tone?: 'plain' | 'draft' | 'removed';

  /** Cells in this row. */
  readonly children: ReactNode;
};

/** One row in a table. */
export const TableRow = memo(function TableRow({ tone = 'plain', children }: TableRowProps) {
  const className = tone === 'draft' ? styles.draft : tone === 'removed' ? styles.removed : undefined;

  return <tr className={className}>{children}</tr>;
});
