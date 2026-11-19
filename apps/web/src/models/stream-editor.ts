import type { StreamGroup } from './stream-group';

/** Editor state for one campaign. */
export type StreamEditor = {
  /** Keitaro campaign id. */
  readonly campaignId: number;

  /** Streams in position order. Empty before the first fetch. */
  readonly streams: readonly StreamGroup[];
};
