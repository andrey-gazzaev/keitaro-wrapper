import type { StreamRowVm } from './stream-row-vm';

/** Rows of the stream editor table. */
export type StreamTableVm = {
  /** Stream and offer rows. Empty before the first fetch. */
  readonly rows: readonly StreamRowVm[];
};
