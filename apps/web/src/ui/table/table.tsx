import { memo, type ReactNode } from 'react';
import styles from './table.module.css';

type TableProps = {
  /** Header row, placed in the table head. */
  readonly head: ReactNode;

  /** Body rows. Empty when the table has no lines yet. */
  readonly children: ReactNode;
};

/** Grid chrome shared by every data table. */
export const Table = memo(function Table({ head, children }: TableProps) {
  return (
    <table className={styles.table}>
      <thead>{head}</thead>
      <tbody>{children}</tbody>
    </table>
  );
});
