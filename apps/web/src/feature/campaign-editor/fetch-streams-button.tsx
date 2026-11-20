import { memo } from 'react';
import { Button } from '@/ui';

type FetchStreamsButtonProps = {
  /** True while the import is in flight. */
  readonly pending: boolean;

  /** Starts an import from Keitaro. */
  readonly onFetch: () => void;
};

/** Button that imports this campaign's flows. */
export const FetchStreamsButton = memo(function FetchStreamsButton({ pending, onFetch }: FetchStreamsButtonProps) {
  return (
    <Button variant="secondary" pending={pending} onClick={onFetch}>
      Fetch Streams
    </Button>
  );
});
