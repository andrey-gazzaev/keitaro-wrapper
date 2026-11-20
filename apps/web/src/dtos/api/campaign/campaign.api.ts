import type { Campaign, CampaignBoard, CampaignDraft } from '@/models';
import { readHttpFailure } from '../../http-failure';
import { api } from '../../http';
import { mapCampaignBoard } from '../../mappers/campaign/map-campaign-board';
import { mapCampaignCreateError } from '../../mappers/campaign/map-campaign-create-error';
import { mapCampaign, mapCampaignDraftDto } from '../../mappers/campaign/map-campaign';
import { campaignBoardSchema } from '../../schemas/campaign/campaign-board.schema';
import { campaignListSchema } from '../../schemas/campaign/campaign-list.schema';
import { campaignSchema } from '../../schemas/campaign/campaign.schema';

/** Loads and changes campaigns stored by the wrapper. */
export class CampaignApi {
  /** Create one campaign and return the stored row. Rejects when the campaign is not created. */
  public async create(draft: CampaignDraft): Promise<Campaign> {
    try {
      const { data } = await api.post('/campaigns', mapCampaignDraftDto(draft));

      return mapCampaign(campaignSchema.parse(data));
    } catch (error) {
      const failure = readHttpFailure(error);

      if (failure === null) {
        throw error;
      }

      throw mapCampaignCreateError(failure);
    }
  }

  /** Every stored campaign, newest first. Empty when nothing is stored. */
  public async list(): Promise<readonly Campaign[]> {
    const { data } = await api.get('/campaigns');

    return campaignListSchema.parse(data).map(mapCampaign);
  }

  /** One page of stored campaigns for this search, newest first. */
  public async board(needle: string, page: number): Promise<CampaignBoard> {
    const { data } = await api.get('/campaigns/board', { params: { q: needle, page } });

    return mapCampaignBoard(campaignBoardSchema.parse(data));
  }

  /** Sync with Keitaro and return every stored campaign, newest first. */
  public async sync(): Promise<readonly Campaign[]> {
    const { data } = await api.post('/campaigns/sync');

    return campaignListSchema.parse(data).map(mapCampaign);
  }
}

/** Shared campaign client. */
export const campaignApi = new CampaignApi();
