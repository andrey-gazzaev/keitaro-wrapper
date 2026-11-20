import type { Campaign } from '@/models';
import type { CampaignRowVm } from '@/view-models';

/** Board line for one stored campaign. */
export function mapCampaignRow(campaign: Campaign): CampaignRowVm {
  return {
    id: campaign.id,
    name: campaign.name,
    deleted: campaign.deleted,
    href: campaign.deleted ? '' : `/campaigns/${campaign.id}`,
  };
}
