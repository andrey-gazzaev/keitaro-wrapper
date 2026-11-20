import type { Offer } from '@/models';
import type { OfferDto } from '../../schemas/offers/offer.schema';

/** Offer from an offer JSON body. */
export function mapOffer(dto: OfferDto): Offer {
  return {
    id: dto.id,
    name: dto.name,
  };
}
