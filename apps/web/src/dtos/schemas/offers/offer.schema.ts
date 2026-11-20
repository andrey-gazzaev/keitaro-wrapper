import { z } from 'zod';

/** Parsed offer body. */
export type OfferDto = {
  /** Keitaro offer id. */
  readonly id: number;

  /** Offer name. Empty when the offer has no name. */
  readonly name: string;
};

/** JSON body of one offer. */
export const offerSchema = z.object({
  id: z.number(),
  name: z.string(),
}) satisfies z.ZodType<OfferDto>;
