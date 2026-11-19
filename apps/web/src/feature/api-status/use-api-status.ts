import { mapApiStatus } from '@/mappers';
import { useHealth } from '@/queries';

/** Label for the health check. `status` is null until the check returns. */
export function useApiStatus() {
  const health = useHealth();

  const status = health.data ? mapApiStatus(health.data) : null;

  return {
    status,
    isLoading: health.isLoading,
    isError: health.isError,
  };
}
