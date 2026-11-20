/** Message for a failed offer search. */
export type OfferFieldErrorVm = {
  /** Message under the offer field. Empty when the search has not failed. */
  readonly offerId: string;
};
