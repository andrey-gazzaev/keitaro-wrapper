import type { CampaignRowVm } from './campaign-row-vm';

/** One page of board lines. */
export type CampaignBoardVm = {
  /** Lines on this page. Empty when the page has no lines. */
  readonly rows: readonly CampaignRowVm[];

  /** Zero-based page. Zero when nothing matches. */
  readonly page: number;

  /** Pages of matches. Zero when nothing matches. */
  readonly pageCount: number;

  /** Empty when there are no campaigns. None when the search misses. Ready when a match exists. */
  readonly state: 'empty' | 'none' | 'ready';
};
