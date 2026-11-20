/** Positive campaign id from a route param. Null when the param is absent or not a positive integer. */
export function campaignIdFromParam(value: string | undefined): number | null {
  if (value === undefined || !/^[1-9]\d*$/.test(value)) {
    return null;
  }

  const campaignId = Number(value);

  if (!Number.isSafeInteger(campaignId)) {
    return null;
  }

  return campaignId;
}
