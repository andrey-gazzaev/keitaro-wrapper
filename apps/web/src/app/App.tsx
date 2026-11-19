import { CampaignEditorPage, HomePage } from '@/views';
import { Providers } from './providers';

/** Application shell. */
export function App() {
  const campaignId = campaignIdFromPath(window.location.pathname);

  return (
    <Providers>
      {campaignId === null ? <HomePage /> : <CampaignEditorPage campaignId={campaignId} />}
    </Providers>
  );
}

function campaignIdFromPath(path: string): number | null {
  const match = /^\/campaigns\/([1-9]\d*)$/.exec(path);

  if (match === null) {
    return null;
  }

  const campaignId = Number(match[1]);

  if (!Number.isSafeInteger(campaignId)) {
    return null;
  }

  return campaignId;
}
