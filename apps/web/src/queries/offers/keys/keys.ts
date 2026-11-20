/** Cache keys for offers. */
export const offerKeys = {
  all: ['offers'] as const,
  search: (text: string) => [...offerKeys.all, 'search', text] as const,
};
