import axios from 'axios';

/** Status and body of a failed HTTP call. */
export type HttpFailure = {
  /** HTTP status. Null when the call received no response. */
  readonly status: number | null;

  /** Response body. Null when the call received no body. */
  readonly body: unknown;
};

/** Status and body of an HTTP client failure. Null when `error` is not an HTTP response failure. */
export function readHttpFailure(error: unknown): HttpFailure | null {
  if (!axios.isAxiosError(error)) {
    return null;
  }

  return {
    status: error.response?.status ?? null,
    body: error.response?.data ?? null,
  };
}
