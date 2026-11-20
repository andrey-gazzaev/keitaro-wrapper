import { Navigate, useParams } from 'react-router-dom';
import { CampaignEditor } from '@/feature/campaign-editor/campaign-editor';
import { Page } from '@/ui';

/** Page for one campaign's stream editor. */
export function CampaignEditorPage() {
  const { campaignId: campaignIdParam } = useParams();

  const campaignId = campaignIdFromParam(campaignIdParam);

  if (campaignId === null) {
    return <Navigate to="/" replace />;
  }

  return (
    <Page>
      <CampaignEditor campaignId={campaignId} />
    </Page>
  );
}

function campaignIdFromParam(value: string | undefined): number | null {
  if (value === undefined || !/^[1-9]\d*$/.test(value)) {
    return null;
  }

  const campaignId = Number(value);

  if (!Number.isSafeInteger(campaignId)) {
    return null;
  }

  return campaignId;
}
