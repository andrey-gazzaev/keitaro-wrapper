import type { Campaign } from '@/models';
import type { CampaignRowVm } from '@/view-models';

/** Board line for one stored campaign. */
export function mapCampaignRow(campaign: Campaign): CampaignRowVm {
  const label = campaign.deleted ? `«${campaign.name}» удалена` : `«${campaign.name}»`;

  return { id: campaign.id, label };
}
