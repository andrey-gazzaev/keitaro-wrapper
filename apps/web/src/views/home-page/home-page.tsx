import { ApiStatus } from '@/feature/api-status/api-status';
import { Page } from '@/ui';

/** First page of the Keitaro wrapper. */
export function HomePage() {
  return (
    <Page>
      <h1>Keitaro</h1>

      <p className="muted">Обёртка над трекером.</p>

      <ApiStatus />
    </Page>
  );
}
