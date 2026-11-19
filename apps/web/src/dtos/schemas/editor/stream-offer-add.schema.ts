import { z } from 'zod';

/** Body sent to add an offer to a stream. */
export type StreamOfferAddDto = {
  /** Keitaro stream id. */
  readonly stream_id: number;

  /** Keitaro offer id. */
  readonly offer_id: number;
};

/** Checks an add-offer body. */
export const streamOfferAddSchema = z.object({
  stream_id: z.number(),
  offer_id: z.number(),
}) satisfies z.ZodType<StreamOfferAddDto>;
