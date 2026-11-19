import { z } from 'zod';

/** Body sent to POST /campaigns. `offer_id` is the Keitaro offer. */
export type CampaignDraftDto = {
  /** Campaign name sent to the API. */
  readonly name: string;

  /** Country code as typed. */
  readonly country: string;

  /** Offer id in Keitaro. */
  readonly offer_id: number;
};

/** Checks a POST /campaigns body. `offer_id` is the Keitaro offer. */
export const campaignDraftSchema = z.object({
  name: z.string(),
  country: z.string(),
  offer_id: z.number(),
}) satisfies z.ZodType<CampaignDraftDto>;
