import { memo, type ReactNode } from 'react';
import styles from './chip.module.css';

type ChipProps = {
  /** Color of the status pill. Neutral is the quiet default. */
  readonly tone?: 'neutral' | 'draft' | 'ok' | 'danger';

  /** Short status text. */
  readonly children: ReactNode;
};

/** Small status pill. */
export const Chip = memo(function Chip({ tone = 'neutral', children }: ChipProps) {
  const className = tone === 'neutral' ? styles.chip : `${styles.chip} ${styles[tone]}`;

  return <span className={className}>{children}</span>;
});
