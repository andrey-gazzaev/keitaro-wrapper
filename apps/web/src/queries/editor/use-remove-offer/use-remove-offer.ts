import { useMutation, useQueryClient } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Archives one live binding and stores the editor. */
export function useRemoveOffer(campaignId: number) {
  const client = useQueryClient();

  return useMutation({
    mutationFn: (bindingId: number) => editorApi.remove(campaignId, bindingId),
    onSuccess: (editor) => {
      client.setQueryData(editorKeys.detail(campaignId), editor);
    },
  });
}
