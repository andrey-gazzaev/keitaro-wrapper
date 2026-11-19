import { useMutation, useQueryClient } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Fixes one offer's share and stores the editor. */
export function usePinOffer(campaignId: number) {
  const client = useQueryClient();

  return useMutation({
    mutationFn: (input: { bindingId: number; share: string }) =>
      editorApi.pin(campaignId, input.bindingId, input.share),
    onSuccess: (editor) => {
      client.setQueryData(editorKeys.detail(campaignId), editor);
    },
  });
}
