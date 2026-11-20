import { createBrowserRouter, Navigate, type RouteObject } from 'react-router-dom';
import { AppShell } from '@/widgets/app-shell/app-shell';
import { CampaignEditorPage, HomePage } from '@/views';

/** Client routes for the wrapper. */
export const routes: RouteObject[] = [
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'campaigns/:campaignId', element: <CampaignEditorPage /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
];

/** Browser history router for the wrapper. */
export const rootRouter = createBrowserRouter(routes);
