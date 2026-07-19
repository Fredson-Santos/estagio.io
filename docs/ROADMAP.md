# estagio.io — Roadmap de Desenvolvimento

Este documento detalha o roteiro de implementação do projeto **estagio.io**, dividido por fases, conforme estabelecido no [Plano de Projeto](PROJECT_PLAN.md).

---

## Fase 1: MVP (Agregador Puro)
*Foco principal: Validar tráfego orgânico (SEO) e entregar valor imediato com agregação centralizada.*

### 1.1 Fundação de Dados
- [x] Definir taxonomia de áreas (lista fixa normalizada)
- [x] Modelagem do banco de dados no PostgreSQL (`jobs`, `sources`, `job_clicks`)
- [x] Configuração do ambiente FastAPI

### 1.2 Pipeline de Dados (Scraping)
- [x] Desenvolver scraper inicial para a Gupy (via endpoints JSON)
- [x] Implementar lógica de deduplicação (filtro de string / similaridade)
- [ ] Desenvolver scrapers secundários (CIEE/Nube, Vagas.com/InfoJobs/Catho)
- [x] Orquestração (n8n ou cron/APScheduler)

### 1.3 Backend (API)
- [ ] Endpoint de listagem de vagas com filtros (área, cidade, modalidade, fonte)
- [ ] Endpoint de detalhes da vaga

### 1.4 Frontend (Astro) e SEO
- [ ] Criar página de listagem (Home) consumindo a API
- [ ] Criar página de detalhe da vaga (SSG/ISR)
- [ ] Implementar schema `JobPosting` e ilha React para botões interativos
- [ ] Configurar `sitemap.xml` e `robots.txt`
- [ ] Criar página "Sobre" para E-E-A-T
- [ ] Verificar propriedade no Google Search Console

### 1.5 Infraestrutura e Analytics
- [ ] Configurar Umami (self-hosted) e instrumentar a tabela `job_clicks`
- [ ] Setup de containerização (Docker + Compose)
- [ ] Deploy na VPS de produção

---

## Fase 2: V1 (Conta e Tracker)
*Foco principal: Retenção de usuários, personalização e controle do processo seletivo.*

- [ ] Sistema de Autenticação (Login com e-mail/senha)
- [ ] Modelagem de banco de dados para `users` e `favorites`/tracker
- [ ] Tracker Pessoal: Lista de vagas salvas com status (inscrito, entrevista, oferta, etc.)
- [ ] Adição Manual de Vaga: Colar link e extrair metadados via OG tags
- [ ] Botão de denúncia ("reportar vaga suspeita")
- [ ] Implementar limites do plano *free* (Freemium)
- [ ] Elaborar e publicar Política de Privacidade (LGPD)

---

## Fase 3: V2 (Diferenciais Avançados)
*Foco principal: Monetização e features baseadas em Inteligência Artificial.*

- [ ] Analisador de Currículo (ATS via IA) baseado na vaga selecionada
- [ ] Sistema de notificações de novas vagas (por área/cidade)
- [ ] Painel Admin: Monitoramento de status das fontes e vagas
- [ ] Integração cuidadosa com novas fontes complexas (ex: LinkedIn)
- [ ] Possível deduplicação avançada por embeddings caso o volume exija
