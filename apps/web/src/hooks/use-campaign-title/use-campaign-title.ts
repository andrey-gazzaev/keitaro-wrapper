import { mapCampaignTitle } from '@/mappers';
import { useCampaigns } from '@/queries';

/** Campaign name for this id. The id text when the list has no such row. Empty when there is no id. */
export function useCampaignTitle(campaignId: number | null): string {
  const query = useCampaigns(campaignId !== null);

  return mapCampaignTitle(query.data ?? [], campaignId);
}
