import { useCallback } from 'react';
import { useSyncCampaigns } from '@/queries';

/** Sync control for the campaign list. */
export function useCampaignSync() {
  const syncCampaigns = useSyncCampaigns();

  const sync = useCallback(() => {
    syncCampaigns.mutate();
  }, [syncCampaigns.mutate]);

  return {
    sync,
    pending: syncCampaigns.isPending,
    failed: syncCampaigns.isError,
  };
}
