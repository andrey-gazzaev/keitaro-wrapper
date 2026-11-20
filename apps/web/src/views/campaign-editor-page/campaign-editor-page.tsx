import { memo, useMemo } from 'react';
import { Navigate, useParams } from 'react-router-dom';
import { CampaignEditor } from '@/feature/campaign-editor/campaign-editor';
import { campaignIdFromParam } from '@/hooks';
import { Page } from '@/ui';

/** Page for one campaign's stream editor. */
export const CampaignEditorPage = memo(function CampaignEditorPage() {
  const { campaignId: campaignIdParam } = useParams();
  const campaignId = campaignIdFromParam(campaignIdParam);

  const editor = useMemo(
    () => (campaignId === null ? null : <CampaignEditor campaignId={campaignId} />),
    [campaignId],
  );

  if (editor === null) {
    return <Navigate to="/" replace />;
  }

  return <Page>{editor}</Page>;
});
