import { memo, type FormEvent } from 'react';
import type { StreamRowVm } from '@/view-models';
import { Button, Input } from '@/ui';
import styles from './stream-share-cell.module.css';

type StreamShareCellProps = {
  /** Offer or stream line this share belongs to. */
  readonly row: StreamRowVm;

  /** Pins the share from the form. */
  readonly onSubmit: (event: FormEvent<HTMLFormElement>) => void;

  /** Returns the offer to the split. */
  readonly onUnpin: () => void;
};

/** Share text, or the pin form for a live offer. */
export const StreamShareCell = memo(function StreamShareCell({ row, onSubmit, onUnpin }: StreamShareCellProps) {
  if (row.pin) {
    return (
      <form className={styles.share} onSubmit={onSubmit}>
        <Input
          name="share"
          key={`${row.bindingId}-${row.share}`}
          defaultValue={row.share}
          aria-label={`Доля ${row.flow}`}
        />
        <Button type="submit" variant="secondary" size="sm">
          Pin
        </Button>
        {row.pinned ? (
          <Button type="button" variant="ghost" size="sm" onClick={onUnpin}>
            Unpin
          </Button>
        ) : null}
      </form>
    );
  }

  if (row.header) {
    return null;
  }

  return row.share;
});
