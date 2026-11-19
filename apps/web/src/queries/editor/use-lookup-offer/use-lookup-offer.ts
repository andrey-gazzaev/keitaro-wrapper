import { useQueryClient } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Looks up one offer by id for this campaign. */
export function useLookupOffer(campaignId: number) {
  const client = useQueryClient();

  async function lookup(offerId: number) {
    return client.fetchQuery({
      queryKey: [...editorKeys.detail(campaignId), 'offer', offerId] as const,
      queryFn: () => editorApi.lookup(campaignId, offerId),
    });
  }

  return { lookup };
}
