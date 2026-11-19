import { useMutation, useQueryClient } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Binds an offer to a stream and stores the editor. */
export function useAddOffer(campaignId: number) {
  const client = useQueryClient();

  return useMutation({
    mutationFn: (input: { streamId: number; offerId: number }) =>
      editorApi.add(campaignId, input.streamId, input.offerId),
    onSuccess: (editor) => {
      client.setQueryData(editorKeys.detail(campaignId), editor);
    },
  });
}
