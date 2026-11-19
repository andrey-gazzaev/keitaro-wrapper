import { useApiStatus } from './use-api-status';

/** Result of the health check. */
export function ApiStatus() {
  const { status, isLoading, isError } = useApiStatus();

  if (isLoading) {
    return <p className="muted">Проверяем API…</p>;
  }

  if (isError || status == null) {
    return <p className="status">API не отвечает.</p>;
  }

  return <p className="status">{status.label}</p>;
}
