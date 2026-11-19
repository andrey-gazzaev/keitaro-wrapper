import type { Health } from '@/models';
import type { ApiStatusVm } from '@/view-models';

/** Home-page sentence for a health check. */
export function mapApiStatus(health: Health): ApiStatusVm {
  return { label: health.ok ? 'API готов.' : 'API не отвечает.' };
}
