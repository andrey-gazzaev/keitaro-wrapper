/** Campaign stored by the wrapper. */
export type Campaign = {
  /** Keitaro campaign id. */
  readonly id: number;

  /** Campaign name. A blank name is rejected and is not stored. */
  readonly name: string;

  /** True when the row is a tombstone. */
  readonly deleted: boolean;
};
