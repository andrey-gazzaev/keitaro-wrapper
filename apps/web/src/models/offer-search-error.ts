type OfferSearchErrorKind = 'unavailable' | 'notConfigured';

/** Why an offer search failed. */
export class OfferSearchError extends Error {
  /** Which failure this is. */
  public readonly kind: OfferSearchErrorKind;

  /** A search that failed this way. */
  public constructor(kind: OfferSearchErrorKind) {
    super();
    this.name = 'OfferSearchError';
    this.kind = kind;
  }
}
