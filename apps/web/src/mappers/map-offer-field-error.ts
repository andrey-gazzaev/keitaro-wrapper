import type { OfferFieldErrorVm } from '@/view-models';

const EMPTY_FIELD_ERROR: OfferFieldErrorVm = {
  offerId: '',
};

/** Message under the offer field for a search failure. Empty when `error` is absent. */
export function mapOfferFieldError(error: unknown): OfferFieldErrorVm {
  if (error == null) {
    return EMPTY_FIELD_ERROR;
  }

  return { offerId: 'Keitaro не ответил' };
}
