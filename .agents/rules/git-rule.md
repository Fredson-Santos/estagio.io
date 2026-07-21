---
trigger: always_on
---

# Regras de Commit Git

1. **Idioma**: Todos os commits devem ser escritos em **Português**.
2. **Estilo**: Devem ser simples, diretos e objetivos.
3. **Padrão de Mensagem**: Seguir o formato `tipo(escopo): descrição` ou `tipo: descrição`.
   - A descrição deve começar com letra minúscula.
   - Não use ponto final ao final da mensagem.
4. **Atomicidade e Granularidade**:
   - **Commits Separados**: Não agrupar modificações massivas em um só commit.
   - **Divisão por Área**: Sempre que houver mudanças em áreas distintas (ex: backend, frontend, docs), realize **commits separados** para cada área.
   - **Unidade Lógica**: Cada commit deve representar uma alteração completa e testável.
5. **Segurança e Prevenção de Vazamentos**:
   - **Verificação Obrigatória**: Antes de qualquer commit, é estritamente obrigatório verificar se não há credenciais, senhas, tokens ou chaves de API nos arquivos sendo commitados.
   - **Arquivos Sensíveis**: Nunca adicione arquivos `.env`, `.env.prod`, ou `.env.local` ao tracking do Git. Certifique-se de que eles estão declarados no `.gitignore`.
   - **Histórico**: Se identificar que um segredo foi adicionado acidentalmente, não faça um novo commit por cima — remova a credencial ou avise para reescrever o histórico.

## Tipos Comuns

- `feat`: Novas funcionalidades.
- `fix`: Correções de bugs.
- `docs`: Alterações em documentação.
- `style`: Mudanças que não afetam o sentido do código (espaços, formatação, etc).
- `refactor`: Alteração de código que não corrige um bug nem adiciona uma funcionalidade.
- `test`: Adição de testes ausentes ou correção de testes existentes.
- `infra`: Alterações em configurações de CI/CD, scripts de deploy, etc.
- `backend`: Mudanças específicas no backend.
- `frontend`: Mudanças específicas no frontend.

## Exemplos Reais do Projeto

- `docs: atualiza README com instruções de execução do projeto`
- `feat(frontend): adiciona página inicial com componentes Astro`
- `style(frontend): formata arquivos .astro e .css na pasta src`
- `fix(frontend): corrige configuração estática no astro.config.mjs`
- `feat: inicializa estrutura do projeto frontend usando Astro`