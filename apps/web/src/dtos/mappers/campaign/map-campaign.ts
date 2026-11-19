import type { Campaign, CampaignDraft } from '@/models';
import type { CampaignDraftDto } from '../../schemas/campaign/campaign-draft.schema';
import type { CampaignDto } from '../../schemas/campaign/campaign.schema';

/** Stored campaign from a campaign JSON body. */
export function mapCampaign(dto: CampaignDto): Campaign {
  return {
    id: dto.id,
    name: dto.name,
    deleted: dto.deleted,
  };
}

/** POST /campaigns body for a create form draft. */
export function mapCampaignDraftDto(draft: CampaignDraft): CampaignDraftDto {
  return {
    name: draft.name,
    country: draft.country,
    offer_id: draft.offerId,
  };
}
