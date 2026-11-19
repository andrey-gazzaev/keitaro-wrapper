import type { Health } from '@/models';
import { api } from '../../http';
import { mapHealth } from '../../mappers/health/map-health';
import { healthSchema } from '../../schemas/health/health.schema';

/** Loads the API health check. */
export class HealthApi {
  /** Whether the API and the database answered. */
  public async load(): Promise<Health> {
    const { data } = await api.get('/health');

    return mapHealth(healthSchema.parse(data));
  }
}

/** Shared health client. */
export const healthApi = new HealthApi();
