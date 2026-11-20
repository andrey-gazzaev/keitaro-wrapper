import type { Campaign, CampaignDraft } from '@/models';
import { readHttpFailure } from '../../http-failure';
import { api } from '../../http';
import { mapCampaignCreateError } from '../../mappers/campaign/map-campaign-create-error';
import { mapCampaign, mapCampaignDraftDto } from '../../mappers/campaign/map-campaign';
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

  /** Sync with Keitaro and return every stored campaign, newest first. */
  public async sync(): Promise<readonly Campaign[]> {
    const { data } = await api.post('/campaigns/sync');

    return campaignListSchema.parse(data).map(mapCampaign);
  }
}

/** Shared campaign client. */
export const campaignApi = new CampaignApi();
