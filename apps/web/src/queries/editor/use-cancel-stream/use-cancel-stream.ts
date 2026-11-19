import { useMutation, useQueryClient } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Drops unpublished bindings and stores the restored editor. */
export function useCancelStream(campaignId: number) {
  const client = useQueryClient();

  return useMutation({
    mutationFn: (streamId: number) => editorApi.cancel(campaignId, streamId),
    onSuccess: (editor) => {
      client.setQueryData(editorKeys.detail(campaignId), editor);
    },
  });
}