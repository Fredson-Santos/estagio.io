# 🔍 Job Extractor API

Extrai informações de vagas de emprego a partir de URLs usando **scraping + LLM**.  
Funciona com Gupy, Indeed, LinkedIn, BeBee, Catho, InfoJobs, Greenhouse, Lever e qualquer outro site.

---

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

```bash
copy .env.example .env
# edite .env com suas credenciais
```

**.env:**
```env
LLM_PROVIDER=gemini          # openai | gemini | openrouter | groq
GEMINI_API_KEY=sua-chave
LLM_MODEL=gemini-2.5-flash   # opcional, usa padrão do provedor se omitido
```

| `LLM_PROVIDER` | Variável de API       | Modelo padrão        |
|----------------|-----------------------|----------------------|
| `openai`       | `OPENAI_API_KEY`      | `gpt-4o-mini`        |
| `gemini`       | `GEMINI_API_KEY`      | `gemini-1.5-flash`   |
| `openrouter`   | `OPENROUTER_API_KEY`  | `openai/gpt-4o-mini` |
| `groq`         | `GROQ_API_KEY`        | `llama3-8b-8192`     |

---

## Iniciar o servidor

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8001
```

Documentação interativa: **http://localhost:8001/docs**

---

## API

### `POST /extract`

Recebe uma URL de vaga e retorna as informações estruturadas.

**Request:**
```http
POST /extract
Content-Type: application/json

{
  "url": "https://cinemark.gupy.io/jobs/10942473"
}
```

**Response `200 OK`:**
```json
{
  "cargo": "Estágio de Desenvolvimento de Software",
  "empresa": "Cinemark",
  "plataforma": "Gupy",
  "localizacao": "São Paulo, SP",
  "modalidade": "Híbrido",
  "tipo_contrato": "Estágio",
  "salario": "Não informado",
  "descricao_resumida": "Vaga de estágio para desenvolvimento de software...",
  "url": "https://cinemark.gupy.io/jobs/10942473",
  "data_extracao": "2026-03-08T18:00:00-03:00"
}
```

**Response com erro de scraping (site bloqueado, URL inválida, etc.):**
```json
{
  "cargo": "N/A",
  "empresa": "N/A",
  "plataforma": "Indeed",
  ...
  "erro": "HTTP 403 ao acessar a URL"
}
```

**Exemplo com curl:**
```bash
curl -X POST http://localhost:8001/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://cinemark.gupy.io/jobs/10942473"}'
```

**Exemplo com Python:**
```python
import requests

r = requests.post("http://localhost:8001/extract", json={
    "url": "https://cinemark.gupy.io/jobs/10942473"
})
print(r.json())
```

---

## Campos retornados

| Campo               | Descrição                                        |
|---------------------|--------------------------------------------------|
| `cargo`             | Título/cargo da vaga                             |
| `empresa`           | Nome da empresa                                  |
| `plataforma`        | Site onde a vaga foi encontrada                  |
| `localizacao`       | Cidade, estado ou Remoto/Híbrido                 |
| `modalidade`        | Presencial / Remoto / Híbrido                    |
| `tipo_contrato`     | CLT / PJ / Estágio / Freelance / Temporário      |
| `salario`           | Faixa salarial (quando disponível)               |
| `descricao_resumida`| Resumo da vaga em 1-2 frases                     |
| `url`               | URL original                                     |
| `data_extracao`     | Timestamp ISO 8601 da extração                   |
| `erro`              | Mensagem de erro (presente apenas em caso de falha) |

---

## Estrutura do projeto

```
job_extractor/
├── api.py             ← Servidor FastAPI (1 endpoint)
├── job_extractor.py   ← Core: scraping + LLM
├── .env               ← Suas credenciais (não versionar)
├── .env.example       ← Template de configuração
└── requirements.txt
```

> **Nota:** Indeed e LinkedIn frequentemente bloqueiam scrapers (HTTP 403).  
> Catho e outros podem ter vagas expiradas (HTTP 404). Nesses casos, o campo `erro` é retornado.
