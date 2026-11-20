import { OfferSearchError } from '@/models';
import type { HttpFailure } from '../../http-failure';

/** Domain failure for a rejected offer search. */
export function mapOfferSearchError(failure: HttpFailure): OfferSearchError {
  if (failure.status === 503) {
    return new OfferSearchError('notConfigured');
  }

  return new OfferSearchError('unavailable');
}
