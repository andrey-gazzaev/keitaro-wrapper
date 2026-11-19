import { useMutation, useQueryClient } from '@tanstack/react-query';
import { campaignApi } from '@/dtos/api/campaign/campaign.api';
import type { CampaignDraft } from '@/models';
import { campaignKeys } from '../keys/keys';

/** Creates a campaign and refreshes the stored list. */
export function useCreateCampaign() {
  const client = useQueryClient();

  return useMutation({
    mutationFn: (draft: CampaignDraft) => campaignApi.create(draft),
    onSuccess: () => {
      void client.invalidateQueries({ queryKey: campaignKeys.all });
    },
  });
}
