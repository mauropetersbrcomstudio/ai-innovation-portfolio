# Clínica Pró Estética — Assistente de Reposição de Insumos

**Status: PROTOTYPE**

Protótipo local atribuído à Clínica Pró Estética a pedido do usuário. Os ativos de marca não fazem parte desta pasta. Esta versão pública não afirma que as regras demonstrativas tenham sido aprovadas pelo cliente.

## Executar localmente

Requer Python 3. Execute nesta pasta:

```bash
python server.py
```

Abra `http://127.0.0.1:8765`. O servidor aceita conexões somente deste computador. Não requer pacotes, conta, chave de API ou conexão externa.

## Fluxo demonstrável

1. Digite uma solicitação sintética ou selecione um exemplo.
2. O protótipo interpreta localmente unidade, insumo, quantidade e urgência por regras e palavras-chave.
3. Revise ou corrija os campos identificados.
4. Consulte os saldos fictícios e a política demonstrativa `DEMO-SUP-01`.
5. Analise a proposta de transferência ou compra simulada na fila.
6. Registre uma decisão humana simulada; os dados permanecem no `localStorage` deste navegador.

## Dados e limites

- Estoques, catálogo, unidades, pedidos iniciais, limites e política são dados sintéticos.
- Não há integração com ERP, estoque, financeiro, fornecedores, agenda, prontuário, WhatsApp ou outros sistemas.
- Não há modelo de IA conectado; a interpretação usa regras locais.
- Aprovar, recusar ou receber altera somente o estado local da demonstração. Nenhuma compra, transferência física ou mensagem acontece.
- O protótipo não autentica usuários nem comprova a identidade de quem registra uma decisão.
- Não inserir dados reais de pacientes, colaboradores, fornecedores ou operações.

Este artefato é um PROTOTYPE local para demonstração controlada, não um sistema produtivo nem evidência de resultado operacional.
