import { memo } from 'react';
import { TableCell, TableRow } from '@/ui';

/** Column titles for the stream table. */
export const StreamTableHead = memo(function StreamTableHead() {
  return (
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
});
