type OfferLookupErrorKind = 'missing' | 'unavailable';

/** Why an offer could not be read. */
export class OfferLookupError extends Error {
  /** Which failure this is. */
  public readonly kind: OfferLookupErrorKind;

  /** A lookup that failed this way. */
  public constructor(kind: OfferLookupErrorKind) {
    super();
    this.name = 'OfferLookupError';
    this.kind = kind;
  }
}
