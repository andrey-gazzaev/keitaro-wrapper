import type { Health } from '@/models';
import type { HealthDto } from '../../schemas/health/health.schema';

/** Whether the API and the database answered. */
export function mapHealth(dto: HealthDto): Health {
  return { ok: dto.status === 'ok' };
}
