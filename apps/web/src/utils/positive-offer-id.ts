/** Positive integer typed in a field. Null when the text is not one. */
export function positiveOfferId(value: string): number | null {
  const trimmed = value.trim();

  if (!/^[1-9]\d*$/.test(trimmed)) {
    return null;
  }

  return Number(trimmed);
}
