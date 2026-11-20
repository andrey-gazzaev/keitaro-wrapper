import { keepPreviousData, useQuery } from '@tanstack/react-query';
import { campaignApi } from '@/dtos/api/campaign/campaign.api';
import { campaignKeys } from '../keys/keys';

/** One page of campaigns for this search text. */
export function useCampaignBoard(needle: string, page: number) {
  return useQuery({
    queryKey: campaignKeys.boardPage(needle, page),
    queryFn: () => campaignApi.board(needle, page),
    placeholderData: keepPreviousData,
  });
}
