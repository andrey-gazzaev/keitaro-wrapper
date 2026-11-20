import { memo, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Card, Chip, Table, TableCell, TableRow } from '@/ui';
import { useCampaignBoard } from './use-campaign-board';
import styles from './campaign-board.module.css';

const campaignHead = (
  <TableRow>
    <TableCell header>Кампания</TableCell>
    <TableCell header>Id</TableCell>
    <TableCell header />
  </TableRow>
);

/** Stored campaigns. */
export const CampaignBoard = memo(function CampaignBoard() {
  const { campaigns, isLoading, isError } = useCampaignBoard();

  const table = useMemo(
    () => (
      <Card>
        <Table head={campaignHead}>
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
    ),
    [campaigns],
  );

  return (
    <>
      {isLoading ? <p className="muted">Загрузка…</p> : null}

      {isError ? <p className="status">Не удалось загрузить кампании.</p> : null}

      {!isLoading && !isError && campaigns.length === 0 ? <p>Кампаний пока нет.</p> : null}

      {campaigns.length > 0 ? table : null}
    </>
  );
});
