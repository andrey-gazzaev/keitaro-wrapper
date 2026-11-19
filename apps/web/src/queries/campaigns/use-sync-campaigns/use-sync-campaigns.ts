import { useMutation, useQueryClient } from '@tanstack/react-query';
import { campaignApi } from '@/dtos/api/campaign/campaign.api';
import { campaignKeys } from '../keys/keys';

/** Syncs campaigns and stores the returned list in the campaign cache. */
export function useSyncCampaigns() {
  const client = useQueryClient();

  return useMutation({
    mutationFn: () => campaignApi.sync(),
    onSuccess: (campaigns) => {
      client.setQueryData(campaignKeys.list(), campaigns);
    },
  });
}
