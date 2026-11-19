import { z } from 'zod';

/** One offer row in an editor body. */
export type StreamLineDto = {
  /** Binding id. */
  readonly id: number;

  /** Keitaro offer id. */
  readonly offer_id: number;

  /** Offer name. Empty when the catalog has no name. */
  readonly name: string;

  /** Working share with two decimal places, such as "37.50". */
  readonly share: string;

  /** True when the working share stays fixed. */
  readonly pinned: boolean;

  /** True when the offer is removed and the row stays. */
  readonly deleted: boolean;
};

/** JSON body of one offer row. */
export const streamLineSchema = z.object({
  id: z.number(),
  offer_id: z.number(),
  name: z.string(),
  share: z.string(),
  pinned: z.boolean(),
  deleted: z.boolean(),
}) satisfies z.ZodType<StreamLineDto>;
