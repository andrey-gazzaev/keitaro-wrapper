import { useQuery } from '@tanstack/react-query';
import { offersApi } from '@/dtos/api/offers/offers.api';
import { offerKeys } from '../keys/keys';

/** Offers whose name or id contains this text. Empty when the text is blank or nothing matches. */
export function useSearchOffers(text: string) {
  return useQuery({
    queryKey: offerKeys.search(text),
    queryFn: () => offersApi.search(text),
    enabled: text.trim() !== '',
  });
}
