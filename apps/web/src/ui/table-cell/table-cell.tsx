import { memo, type ReactNode } from 'react';
import styles from './table-cell.module.css';

type TableCellProps = {
  /** Renders a header cell. */
  readonly header?: boolean;

  /** `end` aligns numbers to the right. */
  readonly align?: 'start' | 'end';

  /** Muted ink for an empty marker such as an em dash. */
  readonly muted?: boolean;

  /** Cell content. Absent for a blank header. */
  readonly children?: ReactNode;
};

/** One header or body cell. */
export const TableCell = memo(function TableCell({
  header = false,
  align = 'start',
  muted = false,
  children,
}: TableCellProps) {
  const className = [styles.cell, header ? styles.header : undefined, align === 'end' ? styles.end : undefined, muted ? styles.muted : undefined]
    .filter((item) => item !== undefined)
    .join(' ');

  if (header) {
    return <th className={className}>{children}</th>;
  }

  return <td className={className}>{children}</td>;
});
