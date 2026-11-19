import type { StreamRowVm } from './stream-row-vm';
import type { StreamTableVm } from './stream-table-vm';

/** Editor screen for one campaign. */
export type CampaignEditorVm = {
  /** Table rows in display order. Empty before the first fetch. */
  readonly table: StreamTableVm;

  /** Live landings streams the add control can select. Empty when none accept an offer. */
  readonly targets: readonly StreamRowVm[];
};
