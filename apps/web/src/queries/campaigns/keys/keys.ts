/** Cache keys for campaigns. */
export const campaignKeys = {
  all: ['campaigns'] as const,
  list: () => [...campaignKeys.all, 'list'] as const,
  board: () => [...campaignKeys.all, 'board'] as const,
  boardPage: (needle: string, page: number) => [...campaignKeys.board(), needle, page] as const,
};
