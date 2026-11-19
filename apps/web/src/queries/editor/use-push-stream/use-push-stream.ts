import { useMutation, useQueryClient } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Replaces the live flow's offers and stores the editor. */
export function usePushStream(campaignId: number) {
  const client = useQueryClient();

  return useMutation({
    mutationFn: (streamId: number) => editorApi.push(campaignId, streamId),
    onSuccess: (editor) => {
      client.setQueryData(editorKeys.detail(campaignId), editor);
    },
  });
}
