import { CampaignSync } from '@/feature/campaign-board/campaign-sync';
import { Button } from '@/ui';

type CampaignCreatorActionsProps = {
  /** True while the create dialog is open. */
  readonly open: boolean;

  /** Opens or closes the create dialog. */
  readonly onToggle: () => void;
};

/** Sync and the control that opens the create dialog. */
export function CampaignCreatorActions({ open, onToggle }: CampaignCreatorActionsProps) {
  return (
    <>
      <CampaignSync disabled={open} />
      <Button variant="primary" disabled={open} onClick={onToggle}>
        Создать кампанию
      </Button>
    </>
  );
}
