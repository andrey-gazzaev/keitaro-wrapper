import { useMutation, useQueryClient } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Imports this campaign's flows and stores the editor. */
export function useFetchStreams(campaignId: number) {
  const client = useQueryClient();

  return useMutation({
    mutationFn: () => editorApi.fetch(campaignId),
    onSuccess: (editor) => {
      client.setQueryData(editorKeys.detail(campaignId), editor);
    },
  });
}
