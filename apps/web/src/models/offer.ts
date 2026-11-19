/** Offer the editor can add. */
export type Offer = {
  /** Keitaro offer id. */
  readonly id: number;

  /** Offer name. Empty when Keitaro sends no name. */
  readonly name: string;
};
