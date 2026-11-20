import type { StreamLine } from './stream-line';

/** One stream and its offer rows. */
export type StreamGroup = {
  /** Stream id. */
  readonly id: number;

  /** Stream name. Empty when the stream has no name. */
  readonly name: string;

  /** Order of this stream on the campaign. */
  readonly position: number;

  /** True when an offer can be added to this stream. */
  readonly acceptsOffers: boolean;

  /** True when this stream is gone from the campaign. */
  readonly deleted: boolean;

  /** True when this stream's offers differ from the saved offers. */
  readonly dirty: boolean;

  /** Offer rows. Empty when the stream has no offers. */
  readonly lines: readonly StreamLine[];
};
