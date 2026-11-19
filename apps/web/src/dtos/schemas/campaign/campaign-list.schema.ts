import { z } from 'zod';
import { campaignSchema } from './campaign.schema';

/** JSON body of a campaign list. Empty when nothing is stored. */
export const campaignListSchema = z.array(campaignSchema);

/** Parsed campaign list. Empty when nothing is stored. */
export type CampaignListDto = z.infer<typeof campaignListSchema>;
