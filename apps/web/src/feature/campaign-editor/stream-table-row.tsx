import { memo, useCallback, type FormEvent } from 'react';
import type { StreamRowVm } from '@/view-models';
import { Button, TableCell, TableRow } from '@/ui';
import { StreamShareCell } from './stream-share-cell';
import type { StreamActionPending } from './use-campaign-editor';

type StreamTableRowProps = {
  /** Stream or offer line. */
  readonly row: StreamRowVm;

  /** Actions in progress. Every id is null when that action is idle. */
  readonly pending: StreamActionPending;

  /** Archives one live binding. */
  readonly onRemove: (bindingId: number) => void;

  /** Restores one deleted binding. */
  readonly onBringBack: (bindingId: number) => void;

  /** Restores one deleted stream. */
  readonly onBringBackStream: (streamId: number) => void;

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
  pending,
  onRemove,
  onBringBack,
  onBringBackStream,
  onPin,
  onUnpin,
  onPush,
  onCancel,
}: StreamTableRowProps) {
  const remove = useCallback(() => {
    onRemove(row.bindingId);
  }, [onRemove, row.bindingId]);

  const bringBack = useCallback(() => {
    if (row.header) {
      onBringBackStream(row.streamId);

      return;
    }

    onBringBack(row.bindingId);
  }, [onBringBack, onBringBackStream, row.bindingId, row.header, row.streamId]);

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

  const removing = pending.removeId === row.bindingId;
  const bringingBack = row.header
    ? pending.bringBackStreamId === row.streamId
    : pending.bringBackId === row.bindingId;
  const pinning = pending.pinId === row.bindingId;
  const unpinning = pending.unpinId === row.bindingId;
  const pushing = pending.pushId === row.streamId;
  const cancelling = pending.cancelId === row.streamId;

  return (
    <TableRow tone={rowTone(row)}>
      <TableCell>{row.flow}</TableCell>
      <TableCell align={row.header ? 'start' : 'end'}>
        <StreamShareCell
          row={row}
          pinning={pinning}
          unpinning={unpinning}
          onSubmit={submitPin}
          onUnpin={unpin}
        />
      </TableCell>
      <TableCell muted>—</TableCell>
      <TableCell muted>—</TableCell>
      <TableCell>
        {row.remove ? (
          <Button type="button" variant="danger" size="sm" pending={removing} onClick={remove}>
            Remove
          </Button>
        ) : null}
        {row.bringBack ? (
          <Button type="button" variant="ghost" size="sm" pending={bringingBack} onClick={bringBack}>
            Bring back
          </Button>
        ) : null}
        {row.publish ? (
          <Button type="button" variant="primary" size="sm" pending={pushing} onClick={push}>
            Push to KT
          </Button>
        ) : null}
        {row.publish ? (
          <Button type="button" variant="secondary" size="sm" pending={cancelling} onClick={cancel}>
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
