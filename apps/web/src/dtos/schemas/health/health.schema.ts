import { z } from 'zod';

/** Parsed GET /health body. `status` is `ok` when the check passed. */
export type HealthDto = {
  /** `ok` when the API and the database answered. */
  readonly status: 'ok';
};

/** JSON body of GET /health. */
export const healthSchema = z.object({
  status: z.literal('ok'),
}) satisfies z.ZodType<HealthDto>;
