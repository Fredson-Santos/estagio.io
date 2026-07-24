import { describe, it, expect, vi, beforeEach } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';

vi.mock('../lib/api', () => ({
  fetchAdminStats: vi.fn(),
  fetchJobs: vi.fn(),
}));

describe('AdminDashboard Component', () => {
  beforeEach(async () => {
    const api = await import('../lib/api');
    (api.fetchAdminStats as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      total_jobs: 42,
      active_jobs: 38,
      featured_jobs: 4,
      sources: 6,
      last_scraped_at: null,
    });
    (api.fetchJobs as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      items: [
        {
          id: 'job-1',
          title: 'Estágio Backend',
          company: 'ACME',
          location: 'São Paulo',
          area: 'TI_SOFTWARE',
          is_featured: true,
          is_active: true,
        },
        {
          id: 'job-2',
          title: 'Estágio Frontend',
          company: 'Beta',
          location: 'Remoto',
          area: 'DESIGN',
          is_featured: false,
          is_active: true,
        },
      ],
      total: 2,
      skip: 0,
      limit: 100,
    });
  });

  it('renders stat cards and job table', async () => {
    const AdminDashboard = (await import('./AdminDashboard.astro')).default;
    const container = await AstroContainer.create();
    const html = await container.renderToString(AdminDashboard);
    expect(html).toContain('Painel Administrativo');
    expect(html).toContain('Total de Vagas');
    expect(html).toContain('Em Destaque');
    expect(html).toContain('Rodar Scrapers');
    expect(html).toContain('Estágio Backend');
    expect(html).toContain('Estágio Frontend');
    expect(html).toContain('text-amber-400');
  });
});
