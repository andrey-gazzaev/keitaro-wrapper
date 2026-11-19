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

  const view = mapCampaignEditor(editor.data);

  function fetchStreams() {
    fetchStreamsMutation.mutate();
  }

  async function lookup(offerId: number) {
    const offer = await offerLookup.lookup(offerId);

    return offer.name;
  }

  function add(streamId: number, offerId: number) {
    addOffer.mutate({ streamId, offerId });
  }

  function remove(bindingId: number) {
    removeOffer.mutate(bindingId);
  }

  function bringBack(bindingId: number) {
    bringBackOffer.mutate(bindingId);
  }

  function pin(bindingId: number, share: string) {
    pinOffer.mutate({ bindingId, share });
  }

  function unpin(bindingId: number) {
    unpinOffer.mutate(bindingId);
  }

  function push(streamId: number) {
    pushStream.mutate(streamId);
  }

  function cancel(streamId: number) {
    cancelStream.mutate(streamId);
  }

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
