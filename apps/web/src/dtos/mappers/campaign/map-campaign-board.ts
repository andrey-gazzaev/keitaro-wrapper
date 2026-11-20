import type { CampaignBoard } from '@/models';
import type { CampaignBoardDto } from '../../schemas/campaign/campaign-board.schema';
import { mapCampaign } from './map-campaign';

/** Campaign page from a board body. */
export function mapCampaignBoard(dto: CampaignBoardDto): CampaignBoard {
  return {
    campaigns: dto.campaigns.map(mapCampaign),
    page: dto.page,
    pageCount: dto.page_count,
    state: dto.state,
  };
}
