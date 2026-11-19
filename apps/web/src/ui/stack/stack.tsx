import { type FormEvent, type ReactNode } from 'react';
import styles from './stack.module.css';

type StackProps = {
  /** Regions in the column. */
  readonly children: ReactNode;

  /** Element that wraps the column. */
  readonly as?: 'div' | 'form' | 'section';

  /** `start` sizes each child to its content. `stretch` fills the width. */
  readonly variant?: 'start' | 'stretch';

  /** Submit handler for a form stack. Absent when the stack is not a form. */
  readonly onSubmit?: (event: FormEvent<HTMLFormElement>) => void;
};

/** Vertical stack with the theme gap. */
export function Stack({ as = 'div', variant = 'stretch', children, onSubmit }: StackProps) {
  const className = variant === 'start' ? `${styles.stack} ${styles.start}` : styles.stack;

  if (as === 'form') {
    return (
      <form className={className} onSubmit={onSubmit}>
        {children}
      </form>
    );
  }

  if (as === 'section') {
    return <section className={className}>{children}</section>;
  }

  return <div className={className}>{children}</div>;
}
