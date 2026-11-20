/** Campaign stored by the wrapper. */
export type Campaign = {
  /** Keitaro campaign id. */
  readonly id: number;

  /** Campaign name. */
  readonly name: string;

  /** True when the row is a tombstone. */
  readonly deleted: boolean;
};
