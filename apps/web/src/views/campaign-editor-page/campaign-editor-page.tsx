import { CampaignEditor } from '@/feature/campaign-editor/campaign-editor';
import { Page } from '@/ui';

type CampaignEditorPageProps = {
  /** Keitaro campaign id from the path. */
  readonly campaignId: number;
};

/** Page for one campaign's stream editor. */
export function CampaignEditorPage({ campaignId }: CampaignEditorPageProps) {
  return (
    <Page>
      <CampaignEditor campaignId={campaignId} />
    </Page>
  );
}
