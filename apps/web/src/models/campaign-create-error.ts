type CampaignCreateErrorKind = 'invalid' | 'missingSetup' | 'missingOffer' | 'notConfigured' | 'unavailable';

type CampaignDraftField = 'name' | 'country' | 'offerId';

/** Why a campaign was not created. */
export class CampaignCreateError extends Error {
  /** Which failure this is. */
  public readonly kind: CampaignCreateErrorKind;

  /** Draft fields this failure belongs to. Empty when the failure is not about a field. */
  public readonly fields: readonly CampaignDraftField[];

  /** A create that failed this way. */
  public constructor(kind: CampaignCreateErrorKind, fields: readonly CampaignDraftField[] = []) {
    super();
    this.name = 'CampaignCreateError';
    this.kind = kind;
    this.fields = fields;
  }
}
