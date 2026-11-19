/** One campaign line on the board. */
export type CampaignRowVm = {
  /** Keitaro campaign id. */
  readonly id: number;

  /** Line shown on the board. Never empty. Mentions deletion when the campaign is a tombstone. */
  readonly label: string;

  /** Editor path. Empty when the campaign is a tombstone. */
  readonly href: string;
};
