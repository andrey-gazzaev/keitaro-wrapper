import { memo, type ReactNode } from 'react';
import styles from './field.module.css';

type FieldProps = {
  /** Name of the control. */
  readonly label: string;

  /** Help under the control. Hidden when `error` is set. */
  readonly hint?: string;

  /** Failure under the control. Absent when the value is accepted. */
  readonly error?: string;

  /** The input or select. */
  readonly children: ReactNode;
};

/** Label, control, and hint for one value. */
export const Field = memo(function Field({ label, hint, error, children }: FieldProps) {
  return (
    <div className={error ? styles.invalid : styles.field}>
      <label>
        <span>{label}</span>
        {children}
      </label>
      {error ? <p className={styles.error}>{error}</p> : hint ? <p className={styles.hint}>{hint}</p> : null}
    </div>
  );
});
