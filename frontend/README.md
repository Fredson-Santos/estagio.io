# estagio.io — Frontend

Frontend do agregador de vagas de estágio. Construído com **Astro** (SSR via Node adapter) + **Tailwind CSS v4**.

## Desenvolvimento local

```bash
npm install
npm run dev          # http://localhost:4321
```

O backend precisa estar rodando em `http://localhost:8000` (ou defina `BACKEND_URL`).

## Scripts

| Comando            | Ação                                   |
| ------------------ | -------------------------------------- |
| `npm run dev`      | Servidor de desenvolvimento            |
| `npm run build`    | Build de produção (`dist/`)            |
| `npm run preview`  | Pré-visualização do build              |
| `npm run test`     | Testes unitários (Vitest)              |

## Variáveis de ambiente

| Variável      | Descrição                                  | Padrão                  |
| ------------- | ------------------------------------------ | ----------------------- |
| `BACKEND_URL`  | URL do backend FastAPI                      | `http://localhost:8000` |

## Estrutura

```
src/
├── components/    # Componentes Astro
├── layouts/       # Layout raiz
├── lib/           # Helpers (api.ts, types.ts)
├── pages/         # Rotas (index, vagas/, sobre, 404)
├── styles/        # CSS global + Tailwind theme
└── utils/         # Formatadores, sanitização, áreas
```
