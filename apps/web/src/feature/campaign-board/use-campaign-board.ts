import { mapCampaignRow } from '@/mappers';
import { useCampaigns, useSyncCampaigns } from '@/queries';

/** Campaign lines and the sync action. `campaigns` is empty while the list is loading. */
export function useCampaignBoard() {
  const query = useCampaigns();
  const syncCampaigns = useSyncCampaigns();

  const campaigns = (query.data ?? []).map(mapCampaignRow);

  function sync() {
    syncCampaigns.mutate();
  }

  return {
    campaigns,
    isLoading: query.isLoading,
    isError: query.isError,
    syncFailed: syncCampaigns.isError,
    syncing: syncCampaigns.isPending,
    sync,
  };
}
