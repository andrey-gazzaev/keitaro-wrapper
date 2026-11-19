import { z } from 'zod';

/** JSON body of GET /health. */
export const healthSchema = z.object({
  status: z.literal('ok'),
});

/** Parsed GET /health body. `status` is `ok` when the check passed. */
export type HealthDto = z.infer<typeof healthSchema>;
