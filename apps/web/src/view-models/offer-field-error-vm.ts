/** Message for a failed offer lookup. */
export type OfferFieldErrorVm = {
  /** Message under the offer id. Empty when the lookup has not failed. */
  readonly offerId: string;
};
