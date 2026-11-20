import { memo, useCallback, type FormEvent, type ReactNode } from 'react';
import type { StreamRowVm } from '@/view-models';
import { Button, TableCell, TableRow } from '@/ui';
import styles from './stream-table-row.module.css';

type StreamTableRowProps = {
  /** Stream or offer line. */
  readonly row: StreamRowVm;

  /** Archives one live binding. */
  readonly onRemove: (bindingId: number) => void;

  /** Restores one deleted binding. */
  readonly onBringBack: (bindingId: number) => void;

  /** Fixes one offer at this share. */
  readonly onPin: (bindingId: number, share: string) => void;

  /** Returns one offer to the split. */
  readonly onUnpin: (bindingId: number) => void;

  /** Writes the stream's active offers to Keitaro. */
  readonly onPush: (streamId: number) => void;

  /** Drops unpublished bindings and restores the snapshot. */
  readonly onCancel: (streamId: number) => void;
};

/** One stream or offer line, drawn with the shared table row. */
export const StreamTableRow = memo(function StreamTableRow({
  row,
  onRemove,
  onBringBack,
  onPin,
  onUnpin,
  onPush,
  onCancel,
}: StreamTableRowProps) {
  const remove = useCallback(() => {
    onRemove(row.bindingId);
  }, [onRemove, row.bindingId]);

  const bringBack = useCallback(() => {
    onBringBack(row.bindingId);
  }, [onBringBack, row.bindingId]);

  const unpin = useCallback(() => {
    onUnpin(row.bindingId);
  }, [onUnpin, row.bindingId]);

  const push = useCallback(() => {
    onPush(row.streamId);
  }, [onPush, row.streamId]);

  const cancel = useCallback(() => {
    onCancel(row.streamId);
  }, [onCancel, row.streamId]);

  const submitPin = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      const share = String(new FormData(event.currentTarget).get('share') ?? '').trim();
      onPin(row.bindingId, share);
    },
    [onPin, row.bindingId],
  );

  const share = shareCell(row, submitPin, unpin);

  return (
    <TableRow tone={rowTone(row)}>
      <TableCell>{row.flow}</TableCell>
      <TableCell align={row.header ? 'start' : 'end'}>{share}</TableCell>
      <TableCell muted>—</TableCell>
      <TableCell muted>—</TableCell>
      <TableCell>
        {row.remove ? (
          <Button type="button" variant="danger" size="sm" onClick={remove}>
            Remove
          </Button>
        ) : null}
        {row.bringBack ? (
          <Button type="button" variant="ghost" size="sm" onClick={bringBack}>
            Bring back
          </Button>
        ) : null}
        {row.publish ? (
          <Button type="button" variant="primary" size="sm" onClick={push}>
            Push to KT
          </Button>
        ) : null}
        {row.publish ? (
          <Button type="button" variant="secondary" size="sm" onClick={cancel}>
            Cancel
          </Button>
        ) : null}
      </TableCell>
    </TableRow>
  );
});

function rowTone(row: StreamRowVm): 'plain' | 'draft' | 'removed' {
  if (row.deleted) {
    return 'removed';
  }

  if (row.dirty) {
    return 'draft';
  }

  return 'plain';
}

function shareCell(
  row: StreamRowVm,
  onSubmit: (event: FormEvent<HTMLFormElement>) => void,
  onUnpin: () => void,
): ReactNode {
  if (row.pin) {
    return (
      <form className={styles.share} onSubmit={onSubmit}>
        <input
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
}
