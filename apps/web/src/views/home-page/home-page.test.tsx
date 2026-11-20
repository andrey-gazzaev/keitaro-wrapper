import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { HomePage } from './home-page';

const campaignApiMock = vi.hoisted(() => ({
  list: vi.fn(),
  create: vi.fn(),
  sync: vi.fn(),
}));

vi.mock('@/dtos/api/health/health.api', () => ({
  healthApi: {
    load: () => Promise.resolve({ ok: true }),
  },
}));

vi.mock('@/dtos/api/campaign/campaign.api', () => ({
  campaignApi: campaignApiMock,
}));

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });

  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('HomePage', () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    campaignApiMock.list.mockReset();
    campaignApiMock.create.mockReset();
    campaignApiMock.sync.mockReset();
    campaignApiMock.list.mockResolvedValue([]);
  });

  it('shows that the API is ready', async () => {
    renderPage();

    expect(screen.getByRole('heading', { name: 'Keitaro' })).toBeInTheDocument();
    expect(await screen.findByText('API готов.')).toBeInTheDocument();
    expect(await screen.findByText('Кампаний пока нет.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Создать' })).toBeEnabled();
    expect(screen.getByRole('button', { name: 'Синхронизировать' })).toBeInTheDocument();
  });

  it('does not create a campaign when the form is blank', async () => {
    const user = userEvent.setup();

    renderPage();

    await screen.findByText('Кампаний пока нет.');
    await user.click(screen.getByRole('button', { name: 'Создать' }));

    expect(campaignApiMock.create).not.toHaveBeenCalled();
  });

  it('creates a campaign and shows the stored name', async () => {
    const user = userEvent.setup();

    campaignApiMock.create.mockResolvedValue({ id: 1, name: 'Spring', deleted: false });
    renderPage();

    await screen.findByText('Кампаний пока нет.');
    await user.type(screen.getByLabelText('Название'), 'Spring');
    await user.type(screen.getByLabelText('Гео-код'), 'us');
    await user.type(screen.getByLabelText('Id оффера'), '7');
    await user.click(screen.getByRole('button', { name: 'Создать' }));

    expect(campaignApiMock.create).toHaveBeenCalledWith({
      name: 'Spring',
      country: 'us',
      offerId: 7,
    });
    expect(await screen.findByText('Кампания «Spring» создана.')).toBeInTheDocument();
  });

  it('keeps the list when sync fails', async () => {
    const user = userEvent.setup();

    campaignApiMock.list.mockResolvedValue([{ id: 4, name: 'Spring', deleted: false }]);
    campaignApiMock.sync.mockRejectedValue(new Error('down'));
    renderPage();

    expect(await screen.findByText('«Spring»')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Синхронизировать' }));

    expect(await screen.findByText('Не удалось синхронизировать.')).toBeInTheDocument();
    expect(screen.getByText('«Spring»')).toBeInTheDocument();
  });
});
