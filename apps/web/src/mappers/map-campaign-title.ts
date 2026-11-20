import type { Campaign } from '@/models';

/** Campaign name for this id. Empty when there is no id. The id text when the list has no such row. */
export function mapCampaignTitle(campaigns: readonly Campaign[], campaignId: number | null): string {
  if (campaignId === null) {
    return '';
  }

  const campaign = campaigns.find((item) => item.id === campaignId);

  if (campaign === undefined) {
    return String(campaignId);
  }

  return campaign.name;
}
