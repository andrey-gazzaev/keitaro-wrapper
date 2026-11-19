import { z } from 'zod';
import { streamGroupListSchema, type StreamGroupListDto } from './stream-group-list.schema';

/** Editor body for one campaign. */
export type StreamEditorDto = {
  /** Keitaro campaign id. */
  readonly campaign_id: number;

  /** Streams in position order. Empty before the first fetch. */
  readonly streams: StreamGroupListDto;
};

/** JSON body of the stream editor. */
export const streamEditorSchema = z.object({
  campaign_id: z.number(),
  streams: streamGroupListSchema,
}) satisfies z.ZodType<StreamEditorDto>;
