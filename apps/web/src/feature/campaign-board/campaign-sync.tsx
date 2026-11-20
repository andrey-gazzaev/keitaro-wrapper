import { memo, useCallback } from 'react';
import { useSyncCampaigns } from '@/queries';
import { Button } from '@/ui';

type CampaignSyncProps = {
  /** True while another dialog is covering the page. */
  readonly disabled: boolean;
};

/** Button that reloads campaigns from Keitaro. */
export const CampaignSync = memo(function CampaignSync({ disabled }: CampaignSyncProps) {
  const syncCampaigns = useSyncCampaigns();

  const sync = useCallback(() => {
    syncCampaigns.mutate();
  }, [syncCampaigns.mutate]);

  return (
    <>
      <Button variant="secondary" disabled={disabled || syncCampaigns.isPending} onClick={sync}>
        Синхронизировать
      </Button>
      {syncCampaigns.isError ? <p className="status">Не удалось синхронизировать.</p> : null}
    </>
  );
});
