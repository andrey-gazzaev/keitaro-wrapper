import { ApiStatus } from '@/feature/api-status/api-status';
import { CampaignBoard } from '@/feature/campaign-board/campaign-board';
import { CreateCampaign } from '@/feature/create-campaign/create-campaign';
import { Stack } from '@/ui';

/** Health check, create form, and the board of stored campaigns. */
export function CampaignCreator() {
  return (
    <>
      <ApiStatus />

      <Stack as="section">
        <CreateCampaign />

        <CampaignBoard />
      </Stack>
    </>
  );
}
