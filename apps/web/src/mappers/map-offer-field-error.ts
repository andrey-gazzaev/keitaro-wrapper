import { OfferLookupError } from '@/models';
import type { OfferFieldErrorVm } from '@/view-models';

const EMPTY_FIELD_ERROR: OfferFieldErrorVm = {
  offerId: '',
};

/** Message under the offer id for a lookup failure. Empty when `error` is absent. */
export function mapOfferFieldError(error: unknown): OfferFieldErrorVm {
  if (error == null) {
    return EMPTY_FIELD_ERROR;
  }

  if (error instanceof OfferLookupError && error.kind === 'missing') {
    return { offerId: 'Оффер не найден.' };
  }

  return { offerId: 'Keitaro не ответил.' };
}
