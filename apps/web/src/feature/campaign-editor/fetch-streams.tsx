type FetchStreamsProps = {
  /** True while the import is in flight. */
  readonly pending: boolean;

  /** Starts an import from Keitaro. */
  readonly onFetch: () => void;
};

/** Button that imports this campaign's flows. */
export function FetchStreams({ pending, onFetch }: FetchStreamsProps) {
  return (
    <button type="button" onClick={onFetch} disabled={pending}>
      Fetch streams from KT
    </button>
  );
}
