import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { routes } from './router';

const campaignApiMock = vi.hoisted(() => ({
  list: vi.fn(),
  create: vi.fn(),
  sync: vi.fn(),
  board: vi.fn(),
}));

vi.mock('@/dtos/api/health/health.api', () => ({
  healthApi: {
    load: () => Promise.resolve({ ok: true }),
  },
}));

vi.mock('@/dtos/api/campaign/campaign.api', () => ({
  campaignApi: campaignApiMock,
}));

vi.mock('@/dtos/api/editor/editor.api', () => ({
  editorApi: {
    load: () => Promise.resolve({ campaignId: 4, streams: [] }),
  },
}));

function renderAt(path: string) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const router = createMemoryRouter(routes, { initialEntries: [path] });

  return render(
    <QueryClientProvider client={client}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}

describe('routes', () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    campaignApiMock.list.mockReset();
    campaignApiMock.board.mockReset();
    campaignApiMock.list.mockResolvedValue([{ id: 4, name: 'Spring', deleted: false }]);
    campaignApiMock.board.mockResolvedValue({
      campaigns: [{ id: 4, name: 'Spring', deleted: false }],
      page: 0,
      pageCount: 1,
      state: 'ready',
    });
  });

  it('opens a campaign in the editor without a document load', async () => {
    const user = userEvent.setup();

    renderAt('/');

    await user.click(await screen.findByRole('link', { name: 'Открыть' }));

    expect(screen.queryByRole('heading', { name: 'Кампании' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Fetch Streams' })).toBeInTheDocument();
  });

  it('shows the home page for an unknown address', async () => {
    renderAt('/missing');

    expect(await screen.findByRole('heading', { name: 'Кампании' })).toBeInTheDocument();
  });

  it('shows the home page when the campaign id is not a positive integer', async () => {
    renderAt('/campaigns/0');

    expect(await screen.findByRole('heading', { name: 'Кампании' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Fetch Streams' })).not.toBeInTheDocument();
  });
});
