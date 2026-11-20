import { memo, useCallback, useMemo, useState } from 'react';
import { CampaignBoard } from '@/feature/campaign-board/campaign-board';
import { CampaignSync } from '@/feature/campaign-board/campaign-sync';
import { CreateCampaign } from '@/feature/create-campaign/create-campaign';
import { Button, PageHead } from '@/ui';

const CAMPAIGNS_INTRO = 'Черновик живёт здесь. В Keitaro состав уходит только по Push.';

/** Page heading, create dialog, and the board of stored campaigns. */
export const CampaignCreator = memo(function CampaignCreator() {
  const [open, setOpen] = useState(false);

  const openCreate = useCallback(() => {
    setOpen(true);
  }, []);

  const closeCreate = useCallback(() => {
    setOpen(false);
  }, []);

  const actions = useMemo(
    () => (
      <>
        <CampaignSync disabled={open} />
        <Button variant="primary" disabled={open} onClick={openCreate}>
          Создать кампанию
        </Button>
      </>
    ),
    [open, openCreate],
  );

  return (
    <>
      <PageHead title="Кампании" description={CAMPAIGNS_INTRO} actions={actions} />

      <CreateCampaign open={open} onClose={closeCreate} />

      <CampaignBoard />
    </>
  );
});
