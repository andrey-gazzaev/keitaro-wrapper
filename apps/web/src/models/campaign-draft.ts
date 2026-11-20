/** Values the create form sends for one campaign. */
export type CampaignDraft = {
  /** Campaign name. Empty when no name is given. */
  readonly name: string;

  /** Country code. */
  readonly country: string;

  /** Offer id in Keitaro. */
  readonly offerId: number;
};
