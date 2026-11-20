import { memo } from 'react';
import { TableCell, TableRow } from '@/ui';

/** Column titles for the campaign board. */
export const CampaignBoardHead = memo(function CampaignBoardHead() {
  return (
    <TableRow>
      <TableCell header>Кампания</TableCell>
      <TableCell header>Id</TableCell>
      <TableCell header />
    </TableRow>
  );
});
