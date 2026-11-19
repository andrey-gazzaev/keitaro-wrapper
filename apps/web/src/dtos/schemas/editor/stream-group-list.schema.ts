import { z } from 'zod';
import { streamGroupSchema } from './stream-group.schema';

/** JSON body of editor streams. Empty before the first fetch. */
export const streamGroupListSchema = z.array(streamGroupSchema);

/** Parsed editor streams. Empty before the first fetch. */
export type StreamGroupListDto = z.infer<typeof streamGroupListSchema>;
