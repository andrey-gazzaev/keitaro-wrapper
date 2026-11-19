import { useQuery } from '@tanstack/react-query';
import { editorApi } from '@/dtos/api/editor/editor.api';
import { editorKeys } from '../keys/keys';

/** Stored editor for this campaign. Empty before the first fetch. */
export function useLoadEditor(campaignId: number) {
  return useQuery({
    queryKey: editorKeys.detail(campaignId),
    queryFn: () => editorApi.load(campaignId),
  });
}
