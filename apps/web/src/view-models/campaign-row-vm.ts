/** One campaign line on the board. */
export type CampaignRowVm = {
  /** Keitaro campaign id. */
  readonly id: number;

  /** Campaign name. Never empty. */
  readonly name: string;

  /** True when the row is a tombstone and has no editor link. */
  readonly deleted: boolean;

  /** Editor path. Empty when the campaign is a tombstone. */
  readonly href: string;
};
