import { memo } from 'react';
import type { StreamRowVm } from '@/view-models';
import { Card, Table, TableCell, TableRow } from '@/ui';
import { StreamTableRow } from './stream-table-row';

type StreamTableProps = {
  /** Rows in display order. Empty before the first fetch. */
  readonly rows: readonly StreamRowVm[];

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

const streamHead = (
  <TableRow>
    <TableCell header>Flow</TableCell>
    <TableCell header align="end">
      Share
    </TableCell>
    <TableCell header>Stats</TableCell>
    <TableCell header>Trends</TableCell>
    <TableCell header>Action</TableCell>
  </TableRow>
);

/** Flows, shares, and the actions for one campaign. */
export const StreamTable = memo(function StreamTable({
  rows,
  onRemove,
  onBringBack,
  onPin,
  onUnpin,
  onPush,
  onCancel,
}: StreamTableProps) {
  return (
    <Card>
      <Table head={streamHead}>
        {rows.map((row) => (
          <StreamTableRow
            key={row.key}
            row={row}
            onRemove={onRemove}
            onBringBack={onBringBack}
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
