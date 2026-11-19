import { Page } from '@/ui';
import { CampaignCreator } from '@/widgets/campaign-creator/campaign-creator';

/** First page of the Keitaro wrapper. */
export function HomePage() {
  return (
    <Page>
      <h1>Keitaro</h1>

      <p className="muted">Обёртка над трекером.</p>

      <CampaignCreator />
    </Page>
  );
}
