import { memo, type ReactNode } from 'react';
import styles from './button.module.css';

type ButtonProps = {
  /** Visual weight of the control. */
  readonly variant: 'primary' | 'secondary' | 'ghost' | 'danger';

  /** `sm` is the compact control used inside a table. */
  readonly size?: 'md' | 'sm';

  /** Button behavior. Submit posts the surrounding form. */
  readonly type?: 'button' | 'submit';

  /** True while the control cannot be used. */
  readonly disabled?: boolean;

  /** True while this action is in progress. False when the control is idle. */
  readonly pending?: boolean;

  /** Label shown on the control. */
  readonly children: ReactNode;

  /** Click handler. Absent on a submit button. */
  readonly onClick?: () => void;
};

/** One themed button. */
export const Button = memo(function Button({
  variant,
  size = 'md',
  type = 'button',
  disabled = false,
  pending = false,
  children,
  onClick,
}: ButtonProps) {
  const className = [styles.button, styles[variant], size === 'sm' ? styles.sm : undefined]
    .filter((item) => item !== undefined)
    .join(' ');

  return (
    <button
      className={className}
      type={type}
      disabled={disabled || pending}
      aria-busy={pending || undefined}
      onClick={onClick}
    >
      {pending ? <span className={styles.loader} aria-hidden="true" /> : null}
      {children}
    </button>
  );
});
