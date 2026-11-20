import { z } from 'zod';
import { type ValidationIssueDto, validationIssueSchema } from './validation-issue.schema';

/** Validation error body. */
export type ValidationErrorDto = {
  /** Rejected fields. Empty when the body lists none. */
  readonly detail: readonly ValidationIssueDto[];
};

/** JSON body of a validation error. */
export const validationErrorSchema = z.object({
  detail: z.array(validationIssueSchema),
}) satisfies z.ZodType<ValidationErrorDto>;
