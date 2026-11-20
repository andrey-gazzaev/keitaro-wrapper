import { memo, useEffectEvent, useId, useLayoutEffect, useRef, type MouseEvent, type ReactNode, type SyntheticEvent } from 'react';
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
  const dialogRef = useRef<HTMLDialogElement>(null);
  const close = useEffectEvent(() => {
    onClose();
  });

  useLayoutEffect(() => {
    const dialog = dialogRef.current;

    if (dialog === null || dialog.open) {
      return;
    }

    dialog.showModal();

    return () => {
      if (dialog.open) {
        dialog.close();
      }
    };
  }, []);

  function onCancel(event: SyntheticEvent<HTMLDialogElement>) {
    event.preventDefault();
    close();
  }

  function onClick(event: MouseEvent<HTMLDialogElement>) {
    const bounds = event.currentTarget.getBoundingClientRect();
    const inside =
      event.clientX >= bounds.left &&
      event.clientX <= bounds.right &&
      event.clientY >= bounds.top &&
      event.clientY <= bounds.bottom;

    if (!inside) {
      close();
    }
  }

  return (
    <dialog ref={dialogRef} className={styles.dialog} aria-labelledby={titleId} onCancel={onCancel} onClick={onClick}>
      <h2 id={titleId}>{title}</h2>
      {description ? <p className={styles.lead}>{description}</p> : null}
      {children}
    </dialog>
  );
});
