import { useMutation, useQueryClient } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Returns one offer to the split and stores the editor. */
export function useUnpinOffer(campaignId: number) {
  const client = useQueryClient();

  return useMutation({
    mutationFn: (bindingId: number) => editorApi.unpin(campaignId, bindingId),
    onSuccess: (editor) => {
      client.setQueryData(editorKeys.detail(campaignId), editor);
    },
  });
}
