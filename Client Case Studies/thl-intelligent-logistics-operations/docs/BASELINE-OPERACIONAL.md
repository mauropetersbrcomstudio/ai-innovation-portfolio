# THL — Baseline operacional confirmada

**Fonte:** fluxo operacional fornecido e confirmado pelo cliente nesta etapa do projeto.  
**Uso:** referência funcional para o MVP.  
**Regra:** não inferir que sistemas, métricas ou políticas não informados já existem na empresa.

## 1. Solicitação, cotação e planejamento comercial

Dados da demanda:
- Origem e destino.
- Tipo de mercadoria.
- Peso e dimensões / cubagem.
- Valor da nota fiscal.
- Urgência.

Modalidades:
- **Carga dedicada / frete expresso:** atendimento exclusivo para um embarcador, roteiro direto e menor tempo de trânsito.
- **Carga fracionada:** compartilhamento do espaço do veículo com cargas de outros clientes.

Documentos mencionados no fluxo:
- NF-e.
- CT-e.
- MDF-e.

A aplicação poderá registrar referências e status documentais. Não emitirá documentos fiscais.

## 2. Coleta e dimensionamento de frota

Tipos de veículos descritos:
- **Vans:** coletas rápidas, volumes menores, frete expresso e áreas urbanas com restrição.
- **Caminhões Truck:** cargas de médio porte e coleta/distribuição regional ou interurbana.
- **Carretas:** transferências de longa distância, grandes volumes e cargas dedicadas de alta capacidade.

Conferência no embarque:
- Quantidade de volumes.
- Integridade das embalagens.
- Etiquetagem na origem.

Não foram fornecidas capacidades, limites de peso/cubagem ou regras de compatibilidade. Esses parâmetros não serão inventados.

## 3. Triagem, armazenagem e consolidação

Aplicável principalmente a carga fracionada, distribuição e contratos de armazenagem. Cargas dedicadas/expressas podem seguir diretamente da coleta para transferência/entrega.

Atividades:
- Recebimento e conferência contra romaneio.
- Leitura de etiquetas.
- Armazenagem quando contratada.
- Consolidação por região, praça e janela de entrega.

## 4. Transferência rodoviária nacional

Atividades:
- Trânsito entre origem e destino ou entre filiais/terminais.
- Monitoramento da viagem.
- Acompanhamento de SLA.
- Gestão de risco e ocorrências em rota.

Não foram fornecidos valores de SLA, regras de risco, malha, rotas ou eventos de rastreamento.

## 5. Distribuição e entrega final

Atividades:
- Desconsolidação e roteirização local.
- Transferência para veículos menores quando aplicável.
- Descarga e conferência com destinatário.
- Registro de recebedor, assinatura ou comprovante eletrônico (POD).

## 6. Diferenças por modalidade

| Etapa | Fracionada | Dedicada / Expresso | Armazenagem + Distribuição |
|---|---|---|---|
| Coleta | Veículo de coleta urbana/regional | Veículo dimensionado para a carga | Recebimento no armazém THL |
| Terminal / estoque | Triagem e consolidação | Não passa no fluxo direto descrito | Estoque até ordem de saída |
| Transferência | Carga consolidada | Viagem exclusiva e direta | Expedição conforme demanda |
| Entrega | Roteirizada na ponta final | Descarga direta | Distribuição fracionada ou dedicada |

## 7. Estados operacionais propostos para o MVP

Os estados abaixo são estados de acompanhamento da aplicação, não uma afirmação de que a THL já utiliza esses códigos:

1. Solicitação registrada.
2. Em cotação / planejamento.
3. Coleta planejada.
4. Coletada.
5. Em triagem / armazenagem (quando aplicável).
6. Consolidada (quando aplicável).
7. Em transferência.
8. Em distribuição.
9. Entregue — aguardando comprovante (quando aplicável).
10. Concluída.
11. Em ocorrência.
12. Cancelada.

A transição entre estados deve ser registrada pelo usuário. Regras de bloqueio e permissões serão definidas após validação adicional.

## 8. Pontos que continuam pendentes de descoberta

- Sistemas e fornecedores atualmente utilizados.
- Capacidades de veículos e critérios de alocação.
- Definições e metas de SLA.
- Tipos de ocorrência e severidade.
- Regras de armazenagem e endereçamento.
- Campos obrigatórios de documentos e conferência.
- Perfis de usuário e matriz de aprovação.
- Indicadores oficiais e respectivas fórmulas.
- Requisitos de segurança, retenção e compartilhamento de dados.
