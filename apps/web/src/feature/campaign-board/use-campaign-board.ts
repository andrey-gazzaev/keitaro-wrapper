import { useMemo } from 'react';
import { mapCampaignRow } from '@/mappers';
import { useCampaigns } from '@/queries';

/** Campaign lines for the board. `campaigns` is empty while the list is loading. */
export function useCampaignBoard() {
  const query = useCampaigns();

  const campaigns = useMemo(() => (query.data ?? []).map(mapCampaignRow), [query.data]);

  return {
    campaigns,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}
