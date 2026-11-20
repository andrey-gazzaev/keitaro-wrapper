import { z } from 'zod';
import type { CampaignDto } from './campaign.schema';
import { campaignSchema } from './campaign.schema';

/** One page of campaigns for a search. */
export type CampaignBoardDto = {
  /** Campaigns on this page. Empty when nothing matches. */
  readonly campaigns: readonly CampaignDto[];

  /** Zero-based page. Zero when nothing matches. */
  readonly page: number;

  /** Pages of matches. Zero when nothing matches. */
  readonly page_count: number;

  /** Empty when there are no campaigns. None when the search misses. Ready when a match exists. */
  readonly state: 'empty' | 'none' | 'ready';
};

/** JSON body of one campaign page. */
export const campaignBoardSchema = z.object({
  campaigns: z.array(campaignSchema),
  page: z.number(),
  page_count: z.number(),
  state: z.enum(['empty', 'none', 'ready']),
}) satisfies z.ZodType<CampaignBoardDto>;
