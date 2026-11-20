import type { Campaign } from './campaign';

/** One page of campaigns for a search. */
export type CampaignBoard = {
  /** Campaigns on this page. Empty when nothing matches. */
  readonly campaigns: readonly Campaign[];

  /** Zero-based page. Zero when nothing matches. */
  readonly page: number;

  /** Pages of matches. Zero when nothing matches. */
  readonly pageCount: number;

  /** Empty when there are no campaigns. None when the search misses. Ready when a match exists. */
  readonly state: 'empty' | 'none' | 'ready';
};
