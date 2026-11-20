import { memo } from 'react';
import { Link } from 'react-router-dom';
import type { CampaignRowVm } from '@/view-models';
import { Card, Chip, Table, TableCell, TableRow } from '@/ui';
import { CampaignBoardHead } from './campaign-board-head';
import styles from './campaign-board-table.module.css';

type CampaignBoardTableProps = {
  /** Campaign lines. Empty when the board has nothing to show. */
  readonly campaigns: readonly CampaignRowVm[];
};

/** Stored campaigns in a table. */
export const CampaignBoardTable = memo(function CampaignBoardTable({ campaigns }: CampaignBoardTableProps) {
  return (
    <Card>
      <Table head={<CampaignBoardHead />}>
        {campaigns.map((campaign) => (
          <TableRow key={campaign.id}>
            <TableCell>
              {campaign.name}
              {campaign.deleted ? (
                <>
                  {' '}
                  <Chip tone="neutral">удалена</Chip>
                </>
              ) : null}
            </TableCell>
            <TableCell align="end">{campaign.id}</TableCell>
            <TableCell>
              {campaign.href === '' ? null : (
                <Link className={styles.open} to={campaign.href}>
                  Открыть
                </Link>
              )}
            </TableCell>
          </TableRow>
        ))}
      </Table>
    </Card>
  );
});
