# Caminho para integrações futuras

Os quatro protótipos funcionam localmente. Integrações externas dependerão de levantamento com cada cliente, autorização de acesso, regras aprovadas e testes em ambiente controlado. Esta página descreve pontos de extensão, sem afirmar que qualquer integração exista.

| Protótipo | Sistemas a identificar com o cliente | Possível evento de entrada | Ação externa futura sujeita a aprovação |
|---|---|---|---|
| FORMARE | CRM, sistema acadêmico, cadastro de cursos | Interesse em matrícula | Criar ou atualizar pré-matrícula |
| CASA VIVA | E-commerce, OMS, estoque, atendimento | Pedido de devolução | Registrar análise e atualizar atendimento |
| AURORA HOTÉIS | PMS, manutenção, governança | Ocorrência de quarto | Abrir ordem de serviço e sincronizar status |
| TECNOFLEX | ERP, MES, QMS | Registro de desvio | Criar não conformidade e registrar contenção |

## Contrato sugerido

1. Receber um evento com ID externo, origem, data, campos mínimos e versão do esquema.
2. Validar campos, autorização, duplicidade e idempotência antes de processar.
3. Executar regras versionadas e registrar explicações, com revisão humana para exceções.
4. Enviar ação ao sistema externo somente após a decisão permitida e confirmação da capacidade de rollback ou compensação.
5. Registrar resultado e falhas de forma durável, sem guardar segredos ou dados pessoais no histórico de apresentação.

O `localStorage` e o histórico atuais não atendem a autenticação, colaboração, auditoria ou recuperação de produção. Uma integração real exigirá armazenamento apropriado, identidade, controle de acesso, observabilidade, tratamento de falhas e testes de contrato.
