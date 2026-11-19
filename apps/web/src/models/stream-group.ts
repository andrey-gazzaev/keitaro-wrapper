import type { StreamLine } from './stream-line';

/** One stream and its offer rows. */
export type StreamGroup = {
  /** Keitaro stream id. */
  readonly id: number;

  /** Stream name. Empty when Keitaro sends no name. */
  readonly name: string;

  /** Order of this stream on the campaign. */
  readonly position: number;

  /** True when this live landings stream can take an offer. */
  readonly acceptsOffers: boolean;

  /** True when Keitaro no longer returns this stream. */
  readonly deleted: boolean;

  /** True when this stream has unpublished working changes. */
  readonly dirty: boolean;

  /** Offer rows. Empty when the stream has no offers. */
  readonly lines: readonly StreamLine[];
};
