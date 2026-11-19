/** Values the create form sends for one campaign. */
export type CampaignDraft = {
  /** Campaign name. Empty when the field is blank. */
  readonly name: string;

  /** Country code as typed. The server stores the uppercase form. */
  readonly country: string;

  /** Offer id in Keitaro. */
  readonly offerId: number;
};
