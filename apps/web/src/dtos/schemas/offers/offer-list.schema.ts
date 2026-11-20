import { z } from 'zod';
import { offerSchema } from './offer.schema';

/** JSON body of an offer search. Empty when nothing matches. */
export const offerListSchema = z.array(offerSchema);

/** Parsed offer search. Empty when nothing matches. */
export type OfferListDto = z.infer<typeof offerListSchema>;
