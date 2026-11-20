import { memo } from 'react';
import type { StreamRowVm } from '@/view-models';
import { Card, Table } from '@/ui';
import type { StreamActionPending } from './use-campaign-editor';
import { StreamTableHead } from './stream-table-head';
import { StreamTableRow } from './stream-table-row';

type StreamTableProps = {
  /** Rows in display order. Empty before the first fetch. */
  readonly rows: readonly StreamRowVm[];

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

/** Flows, shares, and the actions for one campaign. */
export const StreamTable = memo(function StreamTable({
  rows,
  pending,
  onRemove,
  onBringBack,
  onBringBackStream,
  onPin,
  onUnpin,
  onPush,
  onCancel,
}: StreamTableProps) {
  return (
    <Card>
      <Table head={<StreamTableHead />}>
        {rows.map((row) => (
          <StreamTableRow
            key={row.key}
            row={row}
            pending={pending}
            onRemove={onRemove}
            onBringBack={onBringBack}
            onBringBackStream={onBringBackStream}
            onPin={onPin}
            onUnpin={onUnpin}
            onPush={onPush}
            onCancel={onCancel}
          />
        ))}
      </Table>
    </Card>
  );
});
