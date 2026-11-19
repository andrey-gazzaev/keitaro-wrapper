import { z } from 'zod';

/** Offer body the editor can show. */
export type OfferDto = {
  /** Keitaro offer id. */
  readonly id: number;

  /** Offer name. Empty when Keitaro sends no name. */
  readonly name: string;
};

/** JSON body of one offer. */
export const offerSchema = z.object({
  id: z.number(),
  name: z.string(),
}) satisfies z.ZodType<OfferDto>;
