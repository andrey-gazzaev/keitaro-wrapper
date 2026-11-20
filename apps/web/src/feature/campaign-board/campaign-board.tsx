import { memo, useMemo, useState } from 'react';
import { mapCampaignBoard } from '@/mappers';
import { useCampaignBoard } from '@/queries';
import { CampaignBoardPager } from './campaign-board-pager';
import { CampaignBoardSearch } from './campaign-board-search';
import { CampaignBoardTable } from './campaign-board-table';

/** Stored campaigns. */
export const CampaignBoard = memo(function CampaignBoard() {
  const [needle, setNeedle] = useState('');
  const [page, setPage] = useState(0);
  const query = useCampaignBoard(needle, page);

  const board = useMemo(() => mapCampaignBoard(query.data), [query.data]);
  const shown = query.data !== undefined;

  function onNeedle(value: string) {
    setNeedle(value);
    setPage(0);
  }

  return (
    <>
      {query.data === undefined && query.isLoading ? <p className="muted">Загрузка…</p> : null}

      {query.data === undefined && query.isError ? <p className="status">Не удалось загрузить кампании.</p> : null}

      {shown && board.state !== 'empty' ? <CampaignBoardSearch value={needle} onChange={onNeedle} /> : null}

      {shown && board.state === 'empty' ? <p>Кампаний пока нет.</p> : null}

      {shown && board.state === 'none' ? <p>Ничего не найдено.</p> : null}

      {shown && board.rows.length > 0 ? <CampaignBoardTable campaigns={board.rows} /> : null}

      {shown ? <CampaignBoardPager page={board.page} pageCount={board.pageCount} onPage={setPage} /> : null}
    </>
  );
});
