import { z } from 'zod';
import { streamLineListSchema, type StreamLineListDto } from './stream-line-list.schema';

/** One stream in an editor body. */
export type StreamGroupDto = {
  /** Keitaro stream id. */
  readonly id: number;

  /** Stream name. Empty when Keitaro sends no name. */
  readonly name: string;

  /** Order of this stream on the campaign. */
  readonly position: number;

  /** True when this live landings stream can take an offer. */
  readonly accepts_offers: boolean;

  /** True when Keitaro no longer returns this stream. */
  readonly deleted: boolean;

  /** True when this stream has unpublished working changes. */
  readonly dirty: boolean;

  /** Offer rows. Empty when the stream has no offers. */
  readonly lines: StreamLineListDto;
};

/** JSON body of one stream. */
export const streamGroupSchema = z.object({
  id: z.number(),
  name: z.string(),
  position: z.number(),
  accepts_offers: z.boolean(),
  deleted: z.boolean(),
  dirty: z.boolean(),
  lines: streamLineListSchema,
}) satisfies z.ZodType<StreamGroupDto>;
