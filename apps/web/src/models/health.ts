/** Result of the API health check. */
export type Health = {
  /** True when the API answered and the database accepted a query. */
  readonly ok: boolean;
};
