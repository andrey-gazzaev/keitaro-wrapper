/** Messages for the create-campaign form. */
export type CampaignFormErrorVm = {
  /** Message under the name. Empty when the name is accepted. */
  readonly name: string;

  /** Message under the country. Empty when the country is accepted. */
  readonly country: string;

  /** Message under the offer id. Empty when the offer id is accepted. */
  readonly offerId: string;

  /** Message under the form buttons. Empty when the failure belongs to a field or there is none. */
  readonly form: string;
};
