import { memo } from 'react';
import { ApiStatus } from '@/feature/api-status/api-status';
import { CampaignCrumbs } from '@/feature/campaign-crumbs/campaign-crumbs';

/** Trail and API health in the top bar. */
export const AppShellTop = memo(function AppShellTop() {
  return (
    <>
      <CampaignCrumbs />
      <ApiStatus />
    </>
  );
});
