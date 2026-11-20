import { memo, type FormEvent } from 'react';
import type { StreamRowVm } from '@/view-models';
import { Button, Input } from '@/ui';
import styles from './stream-share-cell.module.css';

type StreamShareCellProps = {
  /** Offer or stream line this share belongs to. */
  readonly row: StreamRowVm;

  /** True while this offer is being pinned. */
  readonly pinning: boolean;

  /** True while this offer is being unpinned. */
  readonly unpinning: boolean;

  /** Pins the share from the form. */
  readonly onSubmit: (event: FormEvent<HTMLFormElement>) => void;

  /** Returns the offer to the split. */
  readonly onUnpin: () => void;
};

/** Share text, or the pin form for a live offer. */
export const StreamShareCell = memo(function StreamShareCell({
  row,
  pinning,
  unpinning,
  onSubmit,
  onUnpin,
}: StreamShareCellProps) {
  if (row.pin) {
    return (
      <form className={styles.share} onSubmit={onSubmit}>
        <Input
          name="share"
          key={`${row.bindingId}-${row.share}`}
          defaultValue={row.share}
          aria-label={`Доля ${row.flow}`}
        />
        <Button type="submit" variant="secondary" size="sm" pending={pinning}>
          Pin
        </Button>
        {row.pinned ? (
          <Button type="button" variant="ghost" size="sm" pending={unpinning} onClick={onUnpin}>
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
