---
name: Auralis System
colors:
  surface: '#fdf8f8'
  surface-dim: '#ddd9d8'
  surface-bright: '#fdf8f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f7f3f2'
  surface-container: '#f1edec'
  surface-container-high: '#ebe7e6'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1c1b1b'
  on-surface-variant: '#444748'
  inverse-surface: '#313030'
  inverse-on-surface: '#f4f0ef'
  outline: '#747878'
  outline-variant: '#c4c7c7'
  surface-tint: '#5f5e5e'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#1c1b1b'
  on-primary-container: '#858383'
  inverse-primary: '#c8c6c5'
  secondary: '#5e5e5e'
  on-secondary: '#ffffff'
  secondary-container: '#e1dfdf'
  on-secondary-container: '#626262'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#1d1b1a'
  on-tertiary-container: '#868381'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e5e2e1'
  primary-fixed-dim: '#c8c6c5'
  on-primary-fixed: '#1c1b1b'
  on-primary-fixed-variant: '#474646'
  secondary-fixed: '#e4e2e2'
  secondary-fixed-dim: '#c7c6c6'
  on-secondary-fixed: '#1b1c1c'
  on-secondary-fixed-variant: '#464747'
  tertiary-fixed: '#e6e1df'
  tertiary-fixed-dim: '#cac6c3'
  on-tertiary-fixed: '#1d1b1a'
  on-tertiary-fixed-variant: '#484645'
  background: '#fdf8f8'
  on-background: '#1c1b1b'
  surface-variant: '#e5e2e1'
typography:
  h1:
    fontFamily: Inter
    fontSize: 64px
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  h2:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  h3:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.6'
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.02em
  button:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1440px
  gutter: 24px
  margin-x: 40px
  header-height: 72px
---

## Brand & Style
O estagio.io é um agregador de vagas de estágio no Brasil. O design é **limpo, direto e funcional** — o foco está 100% na vaga. O tom visual é neutro e profissional, sem excessos decorativos. A interface prioriza legibilidade, densidade de informação controlada e uma navegação sem atrito.

O visual mistura **Minimalismo** com elementos sutis de **Glassmorphism** (header translúcido, cards semi-transparentes). A estética é monocromática por padrão, com uma **cor de destaque coral** usada de forma restrita em ações principais (botões de busca, badges, links, indicadores de status). A escolha deliberada do coral foge do azul padrão do setor (LinkedIn, Indeed).

**Identidade:**
- **Logo:** Wordmark, sem símbolo — "estagio.io" estilizado, font-weight 600, letter-spacing negativo.
- **Tom de voz:** Neutro e direto. Sem personalização de nome nem tom "acolhedor".
- **Tema:** Claro e escuro, com toggle no header.

## Colors
A paleta é dominada por neutros suaves. A interface principal é monocromática para máxima legibilidade. A cor coral (`--c-primary`) é o único acento e deve ser usada com parcimônia:
- Botão primário de candidatura
- Dot de recência nos cards de vaga
- Links ativos e indicadores de status
- **Nunca** como cor de fundo de seções inteiras

## Typography
Fonte principal: **Inter** — uma sans-serif neutra de alta performance. A tipografia é tratada como elemento estrutural.

- **Headlines:** Line-height apertado e letter-spacing negativo para um visual "travado" e arquitetônico.
- **Body:** Prioridade em legibilidade com leading generoso (1.6).
- **Captions/labels:** Ocasionalmente em caixa alta com letter-spacing positivo para denotar metadados (fonte da vaga, badges, timestamps).
- **Badges de fonte:** Usam fonte mono para diferenciar visualmente a origem (Gupy, CIEE, etc).

## Layout & Spacing
O layout segue uma filosofia de **grid fixo centralizado** no viewport (max-width: 1440px, margem lateral de 40px). As páginas do MVP seguem esta estrutura:

### Telas do MVP
1. **Home / Listagem** — Header fixo → Hero com título + subtítulo + tags de fontes → Barra de busca → Filtros (modalidade como pills, área/cidade/fonte como selects) → Grid de cards de vaga (auto-fill, min 280px) → Paginação → Footer.
2. **Detalhe da vaga** — Página própria e indexável com schema `JobPosting`. Descrição completa da vaga + botão de candidatura que redireciona para a fonte original.
3. **Sobre** — Página simples com texto sobre o projeto (reforça E-E-A-T pro SEO).

O espaçamento segue uma escala rítmica de **8px**. Cards usam padding interno de 20px. Seções principais têm margens de 40px entre si.

## Elevation & Depth
Profundidade é criada por **Glassmorphism** e camadas tonais, sem sombras pesadas:

1.  **Level 0 (Base):** Background principal (`--background`).
2.  **Level 1 (Panels/Filtros):** Superfícies levemente mais escuras (`--bg-level-1`) com bordas ultra-leves (`--bg-level-1-border`).
3.  **Level 2 (Cards de vaga):** Superfícies brancas ou semi-transparentes com borda de 1px e sombra extremamente difusa (0px offset, 40px blur, 2% opacidade).

O **header** usa `backdrop-filter: blur(12px)` com fundo semi-transparente para manter o contexto enquanto o usuário faz scroll.

## Shapes
A linguagem de formas equilibra precisão geométrica com suavidade orgânica:
- **Botões e pills:** Full-pill (`border-radius: 9999px`) para filtros, toggles e CTAs.
- **Cards de vaga:** Border-radius de 16px para suavizar o conteúdo técnico.
- **Avatares (inicial da empresa):** Border-radius de 12px.
- **Badges de fonte:** Border-radius de 6px.
- **Inputs de busca:** Full-pill para consistência com os botões.

## Components

### Header
- Sticky no topo, altura de 64px, fundo semi-transparente com `backdrop-filter: blur(12px)`.
- Logo "estagio.io" à esquerda (wordmark, sem símbolo).
- Links de navegação à direita: "vagas", "sobre", toggle de tema (ícone sol/lua dentro de botão circular com borda).
- Links usam estilo Caption (14px, cor muted, hover para cor primária).

### Hero
- Padding-top de 56px, margin-bottom de 40px.
- Título principal (`h1`): 36px mobile → 48px desktop, font-weight 600, letter-spacing -0.025em, caixa baixa ("encontre seu estágio").
- Subtítulo: 16px, cor muted, max-width 36rem.
- Tags de fontes (Gupy, CIEE, Vagas.com, InfoJobs, Catho): badges pequenos com fonte mono, fundo `--c-secondary`, borda `--c-border`, border-radius 6px.

### SearchBar
- Input com ícone de lupa à esquerda, placeholder "buscar por cargo ou empresa".
- Border-radius full-pill, fundo `--bg-level-1`, borda `--c-border`.
- Margin-bottom de 16px.

### FilterBar
- **Linha 1:** Label "modalidade" com ícone de sliders + pills (Presencial, Híbrido, Remoto). Pill ativo tem fundo `--c-primary` com texto branco.
- **Linha 2:** Custom selects para "área", "cidade", "fonte". Cada select é um botão full-pill com dropdown arredondado (border-radius 12px). Opção selecionada recebe fundo `--c-primary`.

### JobCard
- Grid responsivo: `auto-fill, minmax(280px, 1fr)`, gap de 16px.
- Cada card tem: avatar com inicial da empresa (44x44px), badge de fonte (canto superior direito), título da vaga (15px, font-weight 600, 2 linhas max), nome da empresa, localização + modalidade + salário (quando disponível), e footer com timestamp ("há X dias") + dot de recência + ícone de redirect (aparece no hover).
- Hover: borda escurece, card sobe 2px (`translateY(-2px)`), sombra sutil aparece, título muda pra cor primária, ícone de redirect faz slide-in.

### Pagination
- Botões de página (36x36px, border-radius 8px). Página ativa tem fundo `--c-primary` com texto branco.
- Botões de navegação (anterior/próximo) com borda e ícones de chevron.

### Footer
- Separado por borda top de 1px, padding de 32px vertical.
- Logo + copyright à esquerda, links de navegação à direita.

### Página Sobre
- Layout simples com container centralizado, título h1 (2rem), parágrafos em cor muted com line-height 1.6.