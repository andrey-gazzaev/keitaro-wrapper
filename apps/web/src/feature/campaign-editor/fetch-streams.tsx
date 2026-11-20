import { memo } from 'react';
import { Button } from '@/ui';

type FetchStreamsProps = {
  /** True while the import is in flight. */
  readonly pending: boolean;

  /** Starts an import from Keitaro. */
  readonly onFetch: () => void;
};

/** Button that imports this campaign's flows. */
export const FetchStreams = memo(function FetchStreams({ pending, onFetch }: FetchStreamsProps) {
  return (
    <Button variant="secondary" disabled={pending} onClick={onFetch}>
      Fetch Streams
    </Button>
  );
});
