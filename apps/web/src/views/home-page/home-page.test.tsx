import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { HomePage } from './home-page';

vi.mock('@/dtos/api/health/health.api', () => ({
  healthApi: {
    load: () => Promise.resolve({ ok: true }),
  },
}));

function renderPage() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={client}>
      <HomePage />
    </QueryClientProvider>,
  );
}

describe('HomePage', () => {
  it('shows that the API is ready', async () => {
    renderPage();

    expect(screen.getByRole('heading', { name: 'Keitaro' })).toBeInTheDocument();
    expect(await screen.findByText('API готов.')).toBeInTheDocument();
  });
});
