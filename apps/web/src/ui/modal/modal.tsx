import { memo, useEffect, useEffectEvent, useId, type ReactNode } from 'react';
import styles from './modal.module.css';

type ModalProps = {
  /** Dialog title. */
  readonly title: string;

  /** Sentence under the title. Absent when the dialog has none. */
  readonly description?: string;

  /** Dialog body. */
  readonly children: ReactNode;

  /** Closes the dialog. */
  readonly onClose: () => void;
};

/** Overlay dialog. A click on the backdrop or Escape closes it. */
export const Modal = memo(function Modal({ title, description, children, onClose }: ModalProps) {
  const titleId = useId();
  const close = useEffectEvent(() => {
    onClose();
  });

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        close();
      }
    }

    document.addEventListener('keydown', onKey);

    return () => {
      document.removeEventListener('keydown', onKey);
    };
  }, [close]);

  return (
    <div className={styles.layer} onClick={onClose} role="presentation">
      <div
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(event) => event.stopPropagation()}
      >
        <h2 id={titleId}>{title}</h2>
        {description ? <p className={styles.lead}>{description}</p> : null}
        {children}
      </div>
    </div>
  );
});
