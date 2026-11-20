import { memo } from 'react';
import { Page } from '@/ui';
import { CampaignCreator } from '@/widgets/campaign-creator/campaign-creator';

const content = <CampaignCreator />;

/** First page of the Keitaro wrapper. */
export const HomePage = memo(function HomePage() {
  return <Page>{content}</Page>;
});
