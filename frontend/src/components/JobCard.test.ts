import { describe, it, expect } from 'vitest';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import JobCard from './JobCard.astro';

describe('JobCard Component', () => {
  it('renders job title, company, location and modality badge correctly', async () => {
    const container = await AstroContainer.create();

    const props = {
      id: 'job-123-abc',
      title: 'Estágio em Engenharia de Software',
      company: 'TechCorp Brasil',
      location: 'São Paulo, SP',
      modality: 'REMOTE',
      salary: 'R$ 2.500/mês',
      publishedAt: 'Hoje',
      isNew: true,
    };

    const html = await container.renderToString(JobCard, { props });

    expect(html).toContain('Estágio em Engenharia de Software');
    expect(html).toContain('TechCorp Brasil');
    expect(html).toContain('São Paulo, SP');
    expect(html).toContain('Remoto');
    expect(html).toContain('R$ 2.500/mês');
    expect(html).toContain('/vagas/job-123-abc');
    expect(html).toContain('Novo');
    // Valida que não contém elementos button aninhados
    expect(html).not.toContain('<button');
  });
});
