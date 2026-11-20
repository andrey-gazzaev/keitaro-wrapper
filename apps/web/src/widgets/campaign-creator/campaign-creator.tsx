import { memo, useCallback, useState } from 'react';
import { CampaignBoard } from '@/feature/campaign-board/campaign-board';
import { CreateCampaign } from '@/feature/create-campaign/create-campaign';
import { PageHead } from '@/ui';
import { CampaignCreatorActions } from './campaign-creator-actions';

const CAMPAIGNS_INTRO = 'Черновик живёт здесь. В Keitaro состав уходит только по Push.';

/** Page heading, create dialog, and the board of stored campaigns. */
export const CampaignCreator = memo(function CampaignCreator() {
  const [open, setOpen] = useState(false);

  const toggleOpen = useCallback(() => {
    setOpen((current) => !current);
  }, []);

  return (
    <>
      <PageHead
        title="Кампании"
        description={CAMPAIGNS_INTRO}
        actions={<CampaignCreatorActions open={open} onToggle={toggleOpen} />}
      />

      <CreateCampaign open={open} onClose={toggleOpen} />

      <CampaignBoard />
    </>
  );
});
