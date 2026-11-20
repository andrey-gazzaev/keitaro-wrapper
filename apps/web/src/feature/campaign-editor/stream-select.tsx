import type { ChangeEvent } from 'react';
import type { StreamRowVm } from '@/view-models';

type StreamSelectProps = {
  /** Live landings streams. Empty when none can take an offer. */
  readonly targets: readonly StreamRowVm[];

  /** Selected stream id. Null when there is nothing to select. */
  readonly selected: number | null;

  /** Stores the chosen stream. */
  readonly onStream: (event: ChangeEvent<HTMLSelectElement>) => void;
};

/** Stream picker for the add-offer form. */
export function StreamSelect({ targets, selected, onStream }: StreamSelectProps) {
  return (
    <select value={selected ?? ''} onChange={onStream} disabled={targets.length === 0}>
      {targets.map((target) => (
        <option key={target.streamId} value={target.streamId}>
          {target.flow === '' ? target.streamId : target.flow}
        </option>
      ))}
    </select>
  );
}
