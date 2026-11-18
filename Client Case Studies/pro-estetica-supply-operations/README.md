# Assistente de Operações — Reposição de Insumos

Case real desenvolvido para a Clínica Pró Estética. Este protótipo funcional foi preparado para aprovação antes das integrações com as plataformas finais e do go-live. Ele demonstra um copiloto que recebe solicitações internas, consulta uma base fictícia de estoque e regras, propõe transferências ou compras e registra decisões humanas.

## Abrir

Com Python 3 instalado, abra um terminal nesta pasta e execute:

```bash
python server.py
```

Depois abra `http://127.0.0.1:8765`. O servidor aceita conexões somente deste computador. Não requer pacotes, conta, chave de API ou conexão externa. Também é possível abrir `index.html` diretamente, mas o servidor local mantém a persistência do navegador mais previsível.

## Fluxo demonstrável

1. Escreva uma solicitação ou escolha um exemplo no painel inicial.
2. O assistente interpreta localmente o texto e identifica unidade, insumo, quantidade e urgência.
3. Confira ou corrija os campos identificados.
4. O protótipo consulta os saldos e a política fictícia `DEMO-EST-01` e sugere uma transferência do estoque central, uma compra simulada ou as duas etapas.
5. A equipe analisa o pedido na fila. Exceções pedem justificativa.
6. Aprovações, recebimentos e movimentações atualizam os dados guardados somente no `localStorage` deste navegador.

Solicitações que excedem o saldo central entram em uma segunda etapa de aprovação de compra. O recebimento pode ser simulado depois, concluindo a solicitação. A recusa também fica registrada na fila local.

## Limites

- Não há integração com WhatsApp, ERP, estoque, financeiro, fornecedores, agenda ou prontuário.
- A interpretação de mensagem usa regras e palavras-chave locais; não há modelo de IA conectado.
- Estoques, catálogo, 17 unidades, pedidos iniciais e limites são dados sintéticos. As regras não foram aprovadas pela Pró Estética.
- Aprovar ou receber atualiza apenas o estado local da demonstração. Nenhuma compra, transferência física, mensagem ou atualização externa acontece.
- O protótipo não autentica usuários. O registro local não comprova a identidade de quem clicou.
- Não inserir dados reais de pacientes, colaboradores ou operação.

Use **Reiniciar demonstração** para restaurar os exemplos sintéticos. O botão no cabeçalho exporta uma cópia JSON dos dados demonstrativos atuais.

