/** One offer row on a stream. */
export type StreamLine = {
  /** Binding id. */
  readonly id: number;

  /** Keitaro offer id. */
  readonly offerId: number;

  /** Offer name. Empty when the catalog has no name. */
  readonly name: string;

  /** Working share with two decimal places, such as "37.50". "0.00" when the offer is deleted. */
  readonly share: string;

  /** True when the working share stays fixed. */
  readonly pinned: boolean;

  /** True when the offer is removed and the row stays. */
  readonly deleted: boolean;
};
