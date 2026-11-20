import { useCallback, useMemo } from 'react';
import { mapCampaignEditor } from '@/mappers';
import {
  useAddOffer,
  useBringBackOffer,
  useBringBackStream,
  useCancelStream,
  useFetchStreams,
  useLoadEditor,
  usePinOffer,
  usePushStream,
  useRemoveOffer,
  useUnpinOffer,
} from '@/queries';

/** Ids of the stream actions that are in progress. */
export type StreamActionPending = {
  /** Binding being removed. Null when remove is idle. */
  readonly removeId: number | null;

  /** Binding being restored. Null when that bring-back is idle. */
  readonly bringBackId: number | null;

  /** Binding being pinned. Null when pin is idle. */
  readonly pinId: number | null;

  /** Binding being unpinned. Null when unpin is idle. */
  readonly unpinId: number | null;

  /** Stream being restored. Null when that bring-back is idle. */
  readonly bringBackStreamId: number | null;

  /** Stream being pushed. Null when push is idle. */
  readonly pushId: number | null;

  /** Stream being cancelled. Null when cancel is idle. */
  readonly cancelId: number | null;
};

/** Editor table, add targets, and the actions that change them. */
export function useCampaignEditor(campaignId: number) {
  const editor = useLoadEditor(campaignId);
  const fetchStreamsMutation = useFetchStreams(campaignId);
  const addOffer = useAddOffer(campaignId);
  const removeOffer = useRemoveOffer(campaignId);
  const bringBackOffer = useBringBackOffer(campaignId);
  const bringBackStreamMutation = useBringBackStream(campaignId);
  const pinOffer = usePinOffer(campaignId);
  const unpinOffer = useUnpinOffer(campaignId);
  const pushStream = usePushStream(campaignId);
  const cancelStream = useCancelStream(campaignId);

  const view = useMemo(() => mapCampaignEditor(editor.data), [editor.data]);

  const pending = useMemo(
    (): StreamActionPending => ({
      removeId: pendingId(removeOffer.isPending, removeOffer.variables),
      bringBackId: pendingId(bringBackOffer.isPending, bringBackOffer.variables),
      pinId: pendingId(pinOffer.isPending, pinOffer.variables?.bindingId),
      unpinId: pendingId(unpinOffer.isPending, unpinOffer.variables),
      bringBackStreamId: pendingId(bringBackStreamMutation.isPending, bringBackStreamMutation.variables),
      pushId: pendingId(pushStream.isPending, pushStream.variables),
      cancelId: pendingId(cancelStream.isPending, cancelStream.variables),
    }),
    [
      removeOffer.isPending,
      removeOffer.variables,
      bringBackOffer.isPending,
      bringBackOffer.variables,
      pinOffer.isPending,
      pinOffer.variables,
      unpinOffer.isPending,
      unpinOffer.variables,
      bringBackStreamMutation.isPending,
      bringBackStreamMutation.variables,
      pushStream.isPending,
      pushStream.variables,
      cancelStream.isPending,
      cancelStream.variables,
    ],
  );

  const fetchStreams = useCallback(() => {
    fetchStreamsMutation.mutate();
  }, [fetchStreamsMutation.mutate]);

  const add = useCallback(
    (streamId: number, offerId: number) => {
      addOffer.mutate({ streamId, offerId });
    },
    [addOffer.mutate],
  );

  const remove = useCallback(
    (bindingId: number) => {
      removeOffer.mutate(bindingId);
    },
    [removeOffer.mutate],
  );

  const bringBack = useCallback(
    (bindingId: number) => {
      bringBackOffer.mutate(bindingId);
    },
    [bringBackOffer.mutate],
  );

  const bringBackStream = useCallback(
    (streamId: number) => {
      bringBackStreamMutation.mutate(streamId);
    },
    [bringBackStreamMutation.mutate],
  );

  const pin = useCallback(
    (bindingId: number, share: string) => {
      pinOffer.mutate({ bindingId, share });
    },
    [pinOffer.mutate],
  );

  const unpin = useCallback(
    (bindingId: number) => {
      unpinOffer.mutate(bindingId);
    },
    [unpinOffer.mutate],
  );

  const push = useCallback(
    (streamId: number) => {
      pushStream.mutate(streamId);
    },
    [pushStream.mutate],
  );

  const cancel = useCallback(
    (streamId: number) => {
      cancelStream.mutate(streamId);
    },
    [cancelStream.mutate],
  );

  return {
    loading: editor.isLoading,
    failed: editor.isError || fetchStreamsMutation.isError,
    rows: view.table.rows,
    targets: view.targets,
    fetching: fetchStreamsMutation.isPending,
    adding: addOffer.isPending,
    pending,
    actionFailed:
      addOffer.isError ||
      removeOffer.isError ||
      bringBackOffer.isError ||
      bringBackStreamMutation.isError ||
      pinOffer.isError ||
      unpinOffer.isError ||
      pushStream.isError ||
      cancelStream.isError,
    fetchStreams,
    add,
    remove,
    bringBack,
    bringBackStream,
    pin,
    unpin,
    push,
    cancel,
  };
}

function pendingId(active: boolean, id: number | undefined): number | null {
  if (!active) {
    return null;
  }

  return id ?? null;
}
