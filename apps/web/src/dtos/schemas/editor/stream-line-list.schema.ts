import { z } from 'zod';
import { streamLineSchema } from './stream-line.schema';

/** JSON body of offer rows. Empty when the stream has no offers. */
export const streamLineListSchema = z.array(streamLineSchema);

/** Parsed offer rows. Empty when the stream has no offers. */
export type StreamLineListDto = z.infer<typeof streamLineListSchema>;
