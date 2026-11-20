import type { Offer } from '@/models';
import { readHttpFailure } from '../../http-failure';
import { api } from '../../http';
import { mapOffer } from '../../mappers/offers/map-offer';
import { mapOfferSearchError } from '../../mappers/offers/map-offer-search-error';
import { offerListSchema } from '../../schemas/offers/offer-list.schema';

/** Searches offers by name or id. */
export class OffersApi {
  /** Matching offers. Empty when the text is blank or nothing matches. */
  public async search(text: string): Promise<readonly Offer[]> {
    try {
      const { data } = await api.get('/offers', { params: { q: text } });

      return offerListSchema.parse(data).map(mapOffer);
    } catch (error) {
      const failure = readHttpFailure(error);

      if (failure === null) {
        throw error;
      }

      throw mapOfferSearchError(failure);
    }
  }
}

/** Shared offer client. */
export const offersApi = new OffersApi();
