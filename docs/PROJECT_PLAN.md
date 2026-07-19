# estagio.io — Plano de Projeto

> Este documento substitui a versão anterior. A discussão de fundação mudou
> decisões importantes (stack de frontend, escopo do MVP, estratégia de
> aquisição) em relação ao primeiro rascunho.

## 1. Objetivo

Projeto de portfólio técnico com potencial real de virar produto. Serve
como diferencial em processos seletivos (demonstra scraping/ETL, backend,
frontend orientado a SEO e arquitetura de dados end-to-end) e, se a tração
orgânica validar a ideia, pode evoluir pra plataforma monetizável.

## 2. Público-alvo

Estudante universitário buscando estágio no Brasil, foco geográfico
inicial em São Paulo (com filtro de "remoto" desde o MVP), expansão
nacional planejada para depois da validação.

## 3. Dores que o produto resolve

1. **Fragmentação** — vaga de estágio espalhada em Gupy, LinkedIn, grupos
   de WhatsApp/Telegram, Catho, InfoJobs, CIEE, sites de faculdade.
2. **Ruído e vaga morta** — vaga expirada ou preenchida continua no ar em
   boa parte dos sites concorrentes.
3. **Falta de contexto pro perfil de estudante** — sites genéricos de
   emprego misturam estágio com vaga sênior.
4. **Nenhum lugar rastreia o próprio processo seletivo do usuário** — cada
   estudante controla isso manualmente (planilha, memória) ou não controla.

## 4. Diferenciais

| Prioridade | Diferencial | Fase |
|---|---|---|
| 1 | Agregação real de múltiplas fontes num único lugar, com dedup | MVP |
| 2 | Tracker pessoal de candidatura (status por vaga, inclusive vagas de fora do site) | V1 |
| 3 | Analisador/ajustador de currículo por IA (ATS) com base na vaga escolhida | V2 |

## 5. Identidade de marca

- **Domínio:** estagio.io (já registrado)
- **Instagram:** @estagio.io (já reservado)
- **Logo:** wordmark, sem símbolo — "estagio.io" estilizado
- **Cor de destaque:** coral (`c-coral`) — escolhida deliberadamente para
  fugir do azul, cor "padrão" do setor (LinkedIn, Indeed, maioria dos
  boards de vaga). Uso restrito a ações principais e destaques (botão de
  busca, badges, links); não usar em excesso.
- **Tom de voz:** neutro e direto, foco 100% na vaga, sem personalização
  de nome nem tom "acolhedor"
- **Tema:** claro e escuro, com toggle

## 6. Escopo por fase

### MVP — agregador puro, sem login
- Scraping de Gupy (endpoints JSON públicos), CIEE/Nube, Vagas.com/InfoJobs/Catho
- Busca e filtros: área, cidade, modalidade (presencial/remoto/híbrido), fonte
- Listagem (home) e **página de detalhe indexável** por vaga (SSG/SSR,
  URL própria, schema `JobPosting`)
- Redirecionamento pra candidatura na fonte original (sem captura própria)
- Deduplicação de vagas entre fontes
- Vaga com link quebrado → marcada como "encerrada" (não deletada)
- Analytics: visitas via Umami + cliques em "candidatar-se" por vaga
- `robots.txt` + `sitemap.xml`
- Página "sobre" (reforça E-E-A-T pro SEO e credibilidade)

### V1 — conta e tracker
- Login (e-mail/senha)
- Tracker: lista de vagas salvas com dropdown de status (inscrito,
  entrevista, oferta, contratado, recusado — sem kanban/drag-and-drop
  por ora)
- Adicionar vaga manual: cola link → auto-extrai título/empresa via OG
  tags → editável se a extração falhar
- Limite de vagas salvas no plano free (modelo freemium)
- Botão de "reportar vaga suspeita" (proteção contra golpe/vaga falsa)

### V2 — diferenciais avançados
- Analisador de currículo por IA (ATS) por vaga específica (possível
  gatilho de monetização — feature premium)
- Notificações de vaga nova por área/cidade favorita
- Mais fontes (LinkedIn avaliado com cautela — ver `docs/SCRAPING.md`)
- Painel admin (status das fontes, vagas ativas/inativas)

## 7. Telas do MVP

1. **Home / Listagem** — busca central, filtros (área, cidade, modalidade,
   fonte), grid de cards de vaga com data de publicação visível
2. **Detalhe da vaga** — página própria e indexável, schema `JobPosting`,
   descrição completa, botão de candidatura (redireciona pra fonte)
3. **Sobre** — quem está por trás do projeto, credibilidade/SEO

## 8. Estratégia de aquisição (foco total em orgânico)

- **Google for Jobs**: cada página de detalhe carrega o schema
  `JobPosting` (schema.org) já no HTML servido — não montado via JS no
  cliente. Requisito obrigatório do MVP, não V1.
- **SEO técnico**: `sitemap.xml`, `robots.txt`, Core Web Vitals levados a
  sério (ver decisão de stack na seção 9)
- **Google Search Console**: acompanhar posição/impressões pros termos-alvo
  (ex: "estágio TI São Paulo")
- **Cold start**: focar volume de vagas em SP primeiro pra não lançar com
  site "vazio"; destacar programas de estágio nacionais grandes (Vivo,
  Bradesco etc.) como conteúdo "sempre no ar" mesmo antes do scraper
  escalar
- **Instagram (@estagio.io)**: vídeo de marketing + destaque de vagas de
  programas grandes
- **Tráfego pago**: como reforço, não como canal principal

## 9. Arquitetura e stack

| Camada | Tecnologia | Motivo |
|---|---|---|
| Frontend | **Astro + ilhas React** | Zero JS por padrão, HTML/CSS estático nas páginas de conteúdo (listagem, detalhe) — ótimo pra Core Web Vitals e schema `JobPosting` servido no HTML inicial. Ilhas React só nos componentes interativos (busca, filtros, favoritar). Diferente do Next.js, não depende de infraestrutura proprietária (Vercel) pra performar — roda bem em VPS própria com Nginx/Node simples |
| Backend | **FastAPI** (Python) | API pura consumida pelo Astro; já dominado |
| Banco de dados | **PostgreSQL** | Full-text search nativo resolve busca sem precisar de Elasticsearch no MVP |
| Scraping/ETL | **Python** (`httpx`/`BeautifulSoup`, `Playwright` quando necessário) | Gupy e outras páginas renderizam client-side em partes |
| Dedup | Filtro barato (similaridade de string, ex. `rapidfuzz`) primeiro; embeddings via IA só para pares ambíguos que passam do threshold textual | Mantém custo de API baixo com volume |
| Orquestração do scraping | **n8n** (cron) ou `APScheduler` | Reaproveita padrão do JobTracker |
| Analytics | **Umami** (self-hosted, sem cookie, compatível com LGPD) + tabela própria `job_clicks` | Evita banner de consentimento de cookie; CTR por vaga fica no seu próprio banco |
| Containerização | **Docker + Docker Compose** | Padrão dos outros projetos |
| Deploy | **VPS própria** | Mesma infra usada no OpenPNCP/JobTracker |

### Por que não Next.js
Já testado pelo usuário e percebido como menos performático — o motivo
técnico é que o Next carrega hidratação React mesmo em páginas
majoritariamente estáticas, e boa parte dos recursos que compensam isso
(ISR, otimização de imagem, edge functions) foram desenhados pra
infraestrutura da Vercel. Rodando em VPS própria, perde-se o ganho de
infra sem eliminar o peso de hidratação — o que reforça a escolha do
Astro, que é stack-agnostic por design.

## 10. Modelo de dados (MVP)

```
sources (id, name, type, base_url, last_run_at, status)
jobs (id, title, company, location, modality, area, description,
      source_url, source_id, posted_at, scraped_at, is_active, status)
      -- status: active | closed
job_clicks (id, job_id, clicked_at, referrer)
```

Auth, `users`, `favorites`/tracker ficam fora do MVP — entram na V1.

### Pendência: taxonomia de área
Cada fonte descreve área de forma diferente ("TI" na Gupy, "Tecnologia da
Informação" no Vagas.com etc.). Definir lista fixa de áreas normalizadas
e mapear cada fonte pra essa lista no scraper. **Bloqueante antes da
implementação do modelo de dados final**, mas não bloqueia a
documentação do plano.

## 11. Métricas de sucesso do MVP

- Número de vagas ativas listadas (saúde do agregador)
- Sessões/visitas orgânicas por mês (Umami)
- CTR de candidatura por vaga (`job_clicks` ÷ visualizações)
- Posição média + impressões pros termos-alvo no Google Search Console
  (ex: "estágio TI São Paulo")

## 12. Pendências para V1 (fora do bloqueio do MVP)

- Política de privacidade (LGPD) — mesmo curta, cobrir analytics desde o MVP
- Curadoria/moderação de vaga suspeita — botão de "reportar" pode entrar
  já na V1
- Direito de imagem de logos de empresas nos cards — validar uso

## 13. Roteiro de desenvolvimento (ordem sugerida, quando chegar a hora)

1. Modelagem do banco (`jobs`, `sources`, `job_clicks`) + taxonomia de área
2. Scraper da Gupy (fonte mais fácil) gravando no Postgres
3. Lógica de dedup (filtro de string primeiro)
4. API FastAPI: endpoint de listagem/filtro/detalhe de vaga
5. Astro: página de listagem (SSG/ISR) consumindo a API
6. Astro: página de detalhe com schema `JobPosting`, ilha React de favoritar
7. `sitemap.xml` + `robots.txt` + verificação no Search Console
8. Scraper de CIEE/Nube e Vagas.com/InfoJobs/Catho
9. Umami + tabela `job_clicks` instrumentados
10. Página "sobre"
11. Deploy na VPS (Docker Compose)
12. (V1) Auth, tracker, vaga manual via link
13. (V2) Analisador de currículo por IA, notificações, mais fontes