import { memo, type ReactNode } from 'react';
import styles from './card.module.css';

type CardProps = {
  /** Contents of the surface. */
  readonly children: ReactNode;
};

/** Bordered surface for a table or a panel. */
export const Card = memo(function Card({ children }: CardProps) {
  return <div className={styles.card}>{children}</div>;
});
