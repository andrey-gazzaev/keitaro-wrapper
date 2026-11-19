/** Cache keys for one campaign editor. */
export const editorKeys = {
  all: ['editor'] as const,
  detail: (campaignId: number) => [...editorKeys.all, campaignId] as const,
};
