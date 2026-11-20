import { useMutation, useQueryClient } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Restores one deleted stream and stores the editor. */
export function useBringBackStream(campaignId: number) {
  const client = useQueryClient();

  return useMutation({
    mutationFn: (streamId: number) => editorApi.bringBackStream(campaignId, streamId),
    onSuccess: (editor) => {
      client.setQueryData(editorKeys.detail(campaignId), editor);
    },
  });
}
