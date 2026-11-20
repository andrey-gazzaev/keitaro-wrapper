import { OfferLookupError } from '@/models';
import type { HttpFailure } from '../../http-failure';

/** Domain failure for a rejected offer lookup. */
export function mapOfferLookupError(failure: HttpFailure): OfferLookupError {
  if (failure.status === 404) {
    return new OfferLookupError('missing');
  }

  return new OfferLookupError('unavailable');
}
