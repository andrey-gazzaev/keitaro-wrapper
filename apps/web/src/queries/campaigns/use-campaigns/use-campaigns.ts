import { useQuery } from '@tanstack/react-query';
import { campaignApi } from '@/dtos/api/campaign/campaign.api';
import { campaignKeys } from '../keys/keys';

/** Campaigns stored by the wrapper, newest first. */
export function useCampaigns(enabled: boolean) {
  return useQuery({
    queryKey: campaignKeys.list(),
    queryFn: () => campaignApi.list(),
    enabled,
  });
}
