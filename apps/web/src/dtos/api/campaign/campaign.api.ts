import type { Campaign, CampaignDraft } from '@/models';
import { api } from '../../http';
import { mapCampaign, mapCampaignDraftDto } from '../../mappers/campaign/map-campaign';
import { campaignListSchema } from '../../schemas/campaign/campaign-list.schema';
import { campaignSchema } from '../../schemas/campaign/campaign.schema';

/** Loads and changes campaigns stored by the wrapper. */
export class CampaignApi {
  /** Create one campaign and return the stored row. */
  public async create(draft: CampaignDraft): Promise<Campaign> {
    const { data } = await api.post('/campaigns', mapCampaignDraftDto(draft));

    return mapCampaign(campaignSchema.parse(data));
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
