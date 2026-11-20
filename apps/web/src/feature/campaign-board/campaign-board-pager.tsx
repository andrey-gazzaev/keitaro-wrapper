import { memo, useCallback } from 'react';
import { Button } from '@/ui';
import styles from './campaign-board-pager.module.css';

type CampaignBoardPagerProps = {
  /** Zero-based page on screen. Zero when nothing matches. */
  readonly page: number;

  /** Pages of matches. Zero when nothing matches. */
  readonly pageCount: number;

  /** Stores the page the operator chose. */
  readonly onPage: (page: number) => void;
};

/** Previous and next page. Absent when there are fewer than two pages. */
export const CampaignBoardPager = memo(function CampaignBoardPager({
  page,
  pageCount,
  onPage,
}: CampaignBoardPagerProps) {
  const back = useCallback(() => {
    onPage(page - 1);
  }, [onPage, page]);

  const forward = useCallback(() => {
    onPage(page + 1);
  }, [onPage, page]);

  if (pageCount < 2) {
    return null;
  }

  return (
    <div className={styles.pager}>
      <Button variant="secondary" disabled={page <= 0} onClick={back}>
        Назад
      </Button>
      <span className={styles.page}>
        {page + 1} из {pageCount}
      </span>
      <Button variant="secondary" disabled={page >= pageCount - 1} onClick={forward}>
        Дальше
      </Button>
    </div>
  );
});
