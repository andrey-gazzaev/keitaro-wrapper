import type { CampaignBoard } from '@/models';
import type { CampaignBoardVm } from '@/view-models';
import { mapCampaignRow } from './map-campaign-row';

/** Board lines for one page. No lines when the board is missing. */
export function mapCampaignBoard(board: CampaignBoard | undefined): CampaignBoardVm {
  if (board === undefined) {
    return { rows: [], page: 0, pageCount: 0, state: 'ready' };
  }

  return {
    rows: board.campaigns.map(mapCampaignRow),
    page: board.page,
    pageCount: board.pageCount,
    state: board.state,
  };
}
