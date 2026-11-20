import { memo } from 'react';
import { Outlet } from 'react-router-dom';
import { Shell } from '@/ui';
import { AppShellSide } from './app-shell-side';
import { AppShellTop } from './app-shell-top';

/** Sidebar, trail, and health around the current page. */
export const AppShell = memo(function AppShell() {
  return (
    <Shell side={<AppShellSide />} top={<AppShellTop />}>
      <Outlet />
    </Shell>
  );
});
