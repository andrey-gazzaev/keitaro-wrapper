import { useQuery } from '@tanstack/react-query';
import { healthApi } from '@/dtos/api/health/health.api';
import { healthKeys } from '../keys/keys';

/** Health of the API and the database. */
export function useHealth() {
  return useQuery({
    queryKey: healthKeys.status(),
    queryFn: () => healthApi.load(),
  });
}
