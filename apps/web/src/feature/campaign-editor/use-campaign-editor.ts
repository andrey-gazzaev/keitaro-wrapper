import { useCallback, useMemo } from 'react';
import { mapCampaignEditor } from '@/mappers';
import {
  useAddOffer,
  useBringBackOffer,
  useCancelStream,
  useFetchStreams,
  useLoadEditor,
  useLookupOffer,
  usePinOffer,
  usePushStream,
  useRemoveOffer,
  useUnpinOffer,
} from '@/queries';

/** Editor table, add targets, and the actions that change them. */
export function useCampaignEditor(campaignId: number) {
  const editor = useLoadEditor(campaignId);
  const fetchStreamsMutation = useFetchStreams(campaignId);
  const offerLookup = useLookupOffer(campaignId);
  const addOffer = useAddOffer(campaignId);
  const removeOffer = useRemoveOffer(campaignId);
  const bringBackOffer = useBringBackOffer(campaignId);
  const pinOffer = usePinOffer(campaignId);
  const unpinOffer = useUnpinOffer(campaignId);
  const pushStream = usePushStream(campaignId);
  const cancelStream = useCancelStream(campaignId);

  const view = useMemo(() => mapCampaignEditor(editor.data), [editor.data]);

  const fetchStreams = useCallback(() => {
    fetchStreamsMutation.mutate();
  }, [fetchStreamsMutation.mutate]);

  const lookup = useCallback(
    async (offerId: number) => {
      const offer = await offerLookup.lookup(offerId);

      return offer.name;
    },
    [offerLookup.lookup],
  );

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
    actionFailed:
      addOffer.isError ||
      removeOffer.isError ||
      bringBackOffer.isError ||
      pinOffer.isError ||
      unpinOffer.isError ||
      pushStream.isError ||
      cancelStream.isError,
    fetchStreams,
    lookup,
    add,
    remove,
    bringBack,
    pin,
    unpin,
    push,
    cancel,
  };
}
