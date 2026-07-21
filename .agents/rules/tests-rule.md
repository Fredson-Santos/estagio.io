---
trigger: always_on
---

# Regras de Testes

1. **Obrigatoriedade**: Toda task finalizada deve ter testes automatizados cobrindo o código desenvolvido (componentes, páginas ou utilitários).
2. **Execução Obrigatória**: A task só é considerada concluída quando todos os testes passarem com sucesso (executando `npm run test` ou comando similar configurado).
3. **Mocks e Serviços Externos**: APIs e serviços externos devem ser **sempre mockados**. Nunca dependa de serviços reais na internet para rodar testes.
4. **Isolamento**: Os testes de componentes frontend devem ser isolados, usando mocks para simular o comportamento de dependências e contextos.

## Fluxo de Trabalho Obrigatório

1. Desenvolver a feature, componente ou correção.
2. Escrever/atualizar os testes no diretório correspondente.
3. Executar os testes locais (ex: `npm run test`) e garantir que 100% passam.
4. Só então realizar o commit.