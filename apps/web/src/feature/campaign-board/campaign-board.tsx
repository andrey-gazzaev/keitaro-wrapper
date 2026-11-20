import { memo, useMemo } from 'react';
import { mapCampaignRow } from '@/mappers';
import { useCampaigns } from '@/queries';
import { CampaignBoardTable } from './campaign-board-table';

/** Stored campaigns. */
export const CampaignBoard = memo(function CampaignBoard() {
  const query = useCampaigns();

  const campaigns = useMemo(() => (query.data ?? []).map(mapCampaignRow), [query.data]);

  return (
    <>
      {query.isLoading ? <p className="muted">Загрузка…</p> : null}

      {query.isError ? <p className="status">Не удалось загрузить кампании.</p> : null}

      {!query.isLoading && !query.isError && campaigns.length === 0 ? <p>Кампаний пока нет.</p> : null}

      {campaigns.length > 0 ? <CampaignBoardTable campaigns={campaigns} /> : null}
    </>
  );
});
