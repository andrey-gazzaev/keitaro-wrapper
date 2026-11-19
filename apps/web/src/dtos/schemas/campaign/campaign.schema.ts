import { z } from 'zod';

/** Parsed campaign body. `deleted` is true when the row is a tombstone. */
export type CampaignDto = {
  /** Keitaro campaign id. */
  readonly id: number;

  /** Campaign name. */
  readonly name: string;

  /** True when the row is a tombstone. */
  readonly deleted: boolean;
};

/** JSON body of one campaign. `deleted` is true when the row is a tombstone. */
export const campaignSchema = z.object({
  id: z.number(),
  name: z.string(),
  deleted: z.boolean(),
}) satisfies z.ZodType<CampaignDto>;
