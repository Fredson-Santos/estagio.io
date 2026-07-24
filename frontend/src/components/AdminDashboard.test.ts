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
    (api.fetchJobs as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      items: [FEATURED_JOB, REGULAR_JOB],
      total: 2,
      skip: 0,
      limit: 100,
    });
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

  it('renders the featured filter selector', async () => {
    const html = await renderDashboard();
    expect(html).toContain('Todas as vagas');
    expect(html).toContain('Em destaque');
    expect(html).toContain('id="select-featured"');
  });

  it('shows the star badge for a featured job', async () => {
    const api = await import('../lib/api');
    (api.fetchJobs as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      items: [FEATURED_JOB],
      total: 1,
      skip: 0,
      limit: 100,
    });
    const html = await renderDashboard();
    // Linha da vaga em destaque
    expect(html).toContain('data-featured="true"');
    // Ícone de estrela preenchida + cor âmbar
    expect(html).toContain('text-amber-400');
    expect(html).toContain('>star<');
    // Botão de toggle com aria-pressed verdadeiro
    expect(html).toContain('aria-pressed="true"');
  });

  it('shows the outline star for a non-featured job', async () => {
    const api = await import('../lib/api');
    (api.fetchJobs as unknown as ReturnType<typeof vi.fn>).mockResolvedValue({
      items: [REGULAR_JOB],
      total: 1,
      skip: 0,
      limit: 100,
    });
    const html = await renderDashboard();
    expect(html).toContain('data-featured="false"');
    expect(html).toContain('text-on-surface-variant');
    expect(html).toContain('>grade<');
    expect(html).toContain('aria-pressed="false"');
  });

  it('passes featured=true to fetchJobs when filter is active', async () => {
    const api = await import('../lib/api');
    const fetchJobsSpy = api.fetchJobs as unknown as ReturnType<typeof vi.fn>;
    fetchJobsSpy.mockClear();
    fetchJobsSpy.mockResolvedValue({
      items: [FEATURED_JOB],
      total: 1,
      skip: 0,
      limit: 100,
    });

    await renderDashboard();

    expect(fetchJobsSpy).toHaveBeenCalledTimes(1);
    const arg = fetchJobsSpy.mock.calls[0][0] as string;
    // Sem query string no container, featured não deve estar presente
    expect(arg).toContain('/jobs?');
    expect(arg).not.toContain('featured=true');
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
});
