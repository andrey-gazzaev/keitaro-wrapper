import { memo } from 'react';
import { Button } from '@/ui';
import { useCampaignSync } from './use-campaign-sync';

type CampaignSyncProps = {
  /** True while another dialog is covering the page. */
  readonly disabled: boolean;
};

/** Button that reloads campaigns from Keitaro. */
export const CampaignSync = memo(function CampaignSync({ disabled }: CampaignSyncProps) {
  const { sync, pending, failed } = useCampaignSync();

  return (
    <>
      <Button variant="secondary" disabled={disabled || pending} onClick={sync}>
        Синхронизировать
      </Button>
      {failed ? <p className="status">Не удалось синхронизировать.</p> : null}
    </>
  );
});
