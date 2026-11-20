import { CampaignCreateError } from '@/models';
import type { HttpFailure } from '../../http-failure';
import { validationErrorSchema } from '../../schemas/http/validation-error.schema';

type DraftField = CampaignCreateError['fields'][number];

/** Domain failure for a rejected campaign create. */
export function mapCampaignCreateError(failure: HttpFailure): CampaignCreateError {
  if (failure.status === 422) {
    return new CampaignCreateError('invalid', invalidFields(failure.body));
  }

  if (failure.status === 409) {
    return new CampaignCreateError('missingSetup');
  }

  if (failure.status === 404) {
    return new CampaignCreateError('missingOffer', ['offerId']);
  }

  if (failure.status === 503) {
    return new CampaignCreateError('notConfigured');
  }

  return new CampaignCreateError('unavailable');
}

function invalidFields(body: unknown): readonly DraftField[] {
  const parsed = validationErrorSchema.safeParse(body);

  if (!parsed.success) {
    return [];
  }

  const fields: DraftField[] = [];

  for (const issue of parsed.data.detail) {
    for (const part of issue.loc) {
      const field = draftField(part);

      if (field !== null && !fields.includes(field)) {
        fields.push(field);
      }
    }
  }

  return fields;
}

function draftField(part: string | number): DraftField | null {
  if (part === 'name' || part === 'country') {
    return part;
  }

  if (part === 'offer_id') {
    return 'offerId';
  }

  return null;
}
