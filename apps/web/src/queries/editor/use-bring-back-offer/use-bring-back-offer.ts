import { useMutation, useQueryClient } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Restores one deleted binding and stores the editor. */
export function useBringBackOffer(campaignId: number) {
  const client = useQueryClient();

  return useMutation({
    mutationFn: (bindingId: number) => editorApi.bringBack(campaignId, bindingId),
    onSuccess: (editor) => {
      client.setQueryData(editorKeys.detail(campaignId), editor);
    },
  });
}
