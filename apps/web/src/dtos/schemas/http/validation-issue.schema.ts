import { z } from 'zod';

/** One rejected field in a validation body. */
export type ValidationIssueDto = {
  /** Path of the rejected value. Empty when the body names no path. */
  readonly loc: readonly (string | number)[];
};

/** One entry in a validation error body. */
export const validationIssueSchema = z.object({
  loc: z.array(z.union([z.string(), z.number()])),
}) satisfies z.ZodType<ValidationIssueDto>;
