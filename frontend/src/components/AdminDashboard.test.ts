import { describe, it, expect, vi, beforeEach } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';

vi.mock('../lib/api', () => ({
  fetchAdminStats: vi.fn(),
  fetchJobs: vi.fn(),
}));

const FEATURED_JOB = {
  id: 'job-1',
  title: 'Estágio Backend',
  company: 'ACME',
  location: 'São Paulo',
  area: 'TI_SOFTWARE',
  is_featured: true,
  is_active: true,
};

const REGULAR_JOB = {
  id: 'job-2',
  title: 'Estágio Frontend',
  company: 'Beta',
  location: 'Remoto',
  area: 'DESIGN',
  is_featured: false,
  is_active: true,
};

async function renderDashboard() {
  const AdminDashboard = (await import('./AdminDashboard.astro')).default;
  const container = await AstroContainer.create();
  return container.renderToString(AdminDashboard);
}

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
    // fetchJobs é chamado duas vezes: uma para featured, uma para todas as vagas
    (api.fetchJobs as unknown as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce({ items: [FEATURED_JOB], total: 1, skip: 0, limit: 100 })
      .mockResolvedValueOnce({ items: [FEATURED_JOB, REGULAR_JOB], total: 2, skip: 0, limit: 25 });
  });

  it('renders stat cards and job table', async () => {
    const html = await renderDashboard();
    expect(html).toContain('Painel Administrativo');
    expect(html).toContain('Total de Vagas');
    expect(html).toContain('Em Destaque');
    expect(html).toContain('Rodar Scrapers');
    expect(html).toContain('Estágio Backend');
    expect(html).toContain('Estágio Frontend');
  });

  it('renders two separate sections: featured and all jobs', async () => {
    const html = await renderDashboard();
    expect(html).toContain('id="featured-tbody"');
    expect(html).toContain('id="jobs-tbody"');
    expect(html).toContain('Vagas em Destaque');
    expect(html).toContain('Todas as Vagas');
  });

  it('does not render the featured filter select', async () => {
    const html = await renderDashboard();
    expect(html).not.toContain('id="select-featured"');
    expect(html).not.toContain('Todas as vagas');
  });

  it('shows the featured job in the featured section with amber star', async () => {
    const html = await renderDashboard();
    // A seção de destaque deve ter data-featured="true" e ícone star com cor âmbar
    expect(html).toContain('id="featured-tbody"');
    expect(html).toContain('data-featured="true"');
    expect(html).toContain('text-amber-400');
    expect(html).toContain('>star<');
  });

  it('shows the outline star for a non-featured job in the all-jobs section', async () => {
    const html = await renderDashboard();
    expect(html).toContain('id="jobs-tbody"');
    expect(html).toContain('data-featured="false"');
    expect(html).toContain('text-on-surface-variant');
    expect(html).toContain('>grade<');
  });

  it('renders featured count badge', async () => {
    const html = await renderDashboard();
    expect(html).toContain('id="featured-count-badge"');
  });

  it('passes featured=true to first fetchJobs call', async () => {
    const api = await import('../lib/api');
    const fetchJobsSpy = api.fetchJobs as unknown as ReturnType<typeof vi.fn>;
    fetchJobsSpy.mockClear();
    fetchJobsSpy
      .mockResolvedValueOnce({ items: [], total: 0, skip: 0, limit: 100 })
      .mockResolvedValueOnce({ items: [], total: 0, skip: 0, limit: 25 });

    await renderDashboard();

    expect(fetchJobsSpy).toHaveBeenCalledTimes(2);
    const firstCall = fetchJobsSpy.mock.calls[0][0] as string;
    const secondCall = fetchJobsSpy.mock.calls[1][0] as string;
    expect(firstCall).toContain('featured=true');
    expect(secondCall).not.toContain('featured=true');
  });

  it('toggleFeatured script contains double-click protection (btn.disabled guard)', async () => {
    // O AstroContainer renderiza scripts como referências externas (<script src="...">),
    // não inline. Verificamos o código fonte do componente diretamente.
    const { readFileSync } = await import('node:fs');
    const { resolve } = await import('node:path');
    const source = readFileSync(
      resolve(import.meta.dirname ?? __dirname, './AdminDashboard.astro'),
      'utf-8'
    );
    // Deve conter a guarda de double-click antes do fetch
    expect(source).toContain('btn.disabled');
    // Deve usar finally para sempre reabilitar o botão
    expect(source).toContain('finally');
    // O guard de early return deve existir
    expect(source).toContain('if (!btn || btn.disabled) return');
  });

  it('renders a logout link pointing to /admin/logout', async () => {
    const html = await renderDashboard();
    expect(html).toContain('href="/admin/logout"');
    expect(html).toContain('Sair');
  });
});
