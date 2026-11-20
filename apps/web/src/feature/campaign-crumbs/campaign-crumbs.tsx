import { memo, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { useCampaignTitle } from '@/hooks';
import { campaignIdFromParam } from '@/utils';
import { Crumbs } from '@/ui';

/** Trail for the current page. The campaign name comes from the stored list. */
export const CampaignCrumbs = memo(function CampaignCrumbs() {
  const { campaignId: campaignIdParam } = useParams();
  const campaignId = campaignIdFromParam(campaignIdParam);
  const title = useCampaignTitle(campaignId);

  const items = useMemo(() => {
    if (campaignId === null) {
      return [{ label: 'Кампании' }];
    }

    return [
      { label: 'Кампании', href: '/' },
      { label: title },
    ];
  }, [campaignId, title]);

  return <Crumbs items={items} />;
});
