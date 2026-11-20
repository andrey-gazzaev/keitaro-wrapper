import { memo } from 'react';
import { Navigate, useParams } from 'react-router-dom';
import { Page } from '@/ui';
import { campaignIdFromParam } from '@/utils';
import { CampaignEditor } from '@/widgets/campaign-editor/campaign-editor';

/** Page for one campaign's stream editor. */
export const CampaignEditorPage = memo(function CampaignEditorPage() {
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
});
