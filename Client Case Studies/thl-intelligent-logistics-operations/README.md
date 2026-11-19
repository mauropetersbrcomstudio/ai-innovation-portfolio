# Intelligent Logistics Operations — THL

**Status:** MVP demonstrativo funcional — pronto para validação controlada  
**Tipo de entrega:** aplicação independente para descoberta e acompanhamento operacional  
**Integrações externas:** fora do escopo desta versão

## Contexto confirmado

O fluxo operacional abaixo foi confirmado pelo cliente e constitui a baseline funcional deste projeto:

1. Solicitação, cotação e planejamento comercial.
2. Coleta e dimensionamento de frota.
3. Triagem, armazenagem e consolidação, quando aplicável.
4. Transferência rodoviária nacional.
5. Distribuição, entrega final e comprovação de entrega.

Modalidades contempladas:
- Carga fracionada.
- Carga dedicada / frete expresso.
- Armazenagem + distribuição.

O fluxo detalhado de referência está documentado em [BASELINE-OPERACIONAL.md](./docs/BASELINE-OPERACIONAL.md).

## O que esta versão faz

- Registra cargas e seus dados operacionais manualmente.
- Registra o inventário de sistemas e ferramentas utilizados pela empresa.
- Coleta informações sobre ERP, TMS, WMS, rastreamento, transportadoras, documentos, comunicação e BI.
- Registra ocorrências operacionais e histórico de tratativas.
- Registra metadados e status de documentos de transporte (NF-e, CT-e, MDF-e, romaneio e POD), sem upload ou validação fiscal.
- Registra manualmente eventos de transferência, chegada, distribuição e entrega.
- Registra checklist de coleta: veículo selecionado, volumes previstos/conferidos, integridade, identificação/etiquetas e resultado informado.
- Registra operações de terminal: entrada, manifesto, triagem, armazenagem contratada, consolidação, destino e janela de expedição, incluindo fluxo direto não aplicável.
- Mantém histórico local de eventos e permite exportar os dados em JSON.
- Exibe uma visão geral baseada exclusivamente nos registros inseridos, com contagens de registros operacionais, distribuição por modalidade e previsões de entrega ultrapassadas conforme a data informada (sem presumir SLA contratual).
- Exibe alertas operacionais derivados por regras determinísticas dos registros manuais: previsões informadas ultrapassadas, ocorrências abertas, divergências de coleta/terminal, POD pendente ou divergente e documentos com status de pendência. Os alertas são sinalizações para revisão humana, não previsões, decisões automáticas ou avaliação de SLA.
- Atualiza o status da carga a partir de etapas mapeadas de movimentação e terminal quando a referência corresponde a uma carga cadastrada.
- Ao registrar POD como “Conferido manualmente”, marca a carga vinculada como concluída. Essas transições refletem apenas os registros manuais e podem ser corrigidas pela equipe.
- Sugere referências de cargas já cadastradas nos formulários relacionados, mantendo a possibilidade de digitação manual.

## O que esta versão não faz

- Não conecta a ERP, TMS, WMS, transportadoras, rastreadores, e-mail, WhatsApp ou BI.
- Não consulta dados externos nem transmite informações.
- Não emite NF-e, CT-e ou MDF-e.
- Não contrata fretes, despacha veículos, movimenta estoque físico ou confirma entregas. A atualização de status por movimentação apenas reflete a etapa manual selecionada, não confirma a execução física do evento.
- Não possui autenticação multiusuário nem banco de dados central.
- Não utiliza modelo externo de IA. As classificações e registros são manuais nesta primeira versão.
- Não calcula capacidade de frota nem valida adequação técnica do veículo; o dimensionamento permanece sob responsabilidade operacional.

## Executar localmente

Requer Python 3, sem dependências adicionais.

```bash
python server.py
```

Abra http://127.0.0.1:8766 no mesmo computador. Para encerrar, pressione Ctrl+C no terminal.

Também é possível abrir `index.html` diretamente, mas o servidor local é recomendado.

## Persistência e privacidade

Os registros desta versão ficam no armazenamento local do navegador (`localStorage`) do computador utilizado. Não são sincronizados entre computadores. O botão **Exportar dados** gera um arquivo JSON local.

Não inserir dados pessoais, documentos fiscais reais, dados comerciais sensíveis, credenciais, informações de motoristas ou dados de clientes sem autorização e avaliação de segurança. Para demonstrações, utilizar dados fictícios ou devidamente anonimizados.

## Estado de release e limitações conhecidas

Este pacote entrega um MVP demonstrativo independente, com registros manuais e persistência no navegador. Está apto para demonstração controlada com dados fictícios ou anonimizados, mas não está homologado para operação produtiva.

Antes de uso compartilhado ou produtivo, ainda são necessários:
1. Validar campos, estados, regras de coleta e terminal com as equipes responsáveis.
2. Descobrir sistemas, formatos, integrações e fontes oficiais de dados.
3. Definir autenticação, perfis de acesso, banco central, retenção, backup e trilha de auditoria confiável.
4. Definir regras operacionais, SLA e indicadores oficiais com suas fórmulas e responsáveis.
5. Avaliar segurança, privacidade, requisitos legais e continuidade operacional.
6. Planejar integrações e eventual uso de IA somente após a qualidade e governança dos dados serem avaliadas.

## Integridade e autorização do case

A confirmação do fluxo operacional não representa confirmação de indicadores, volumes, sistemas utilizados, regras internas, resultados ou autorização para publicação pública do nome e logotipo do cliente. A publicação identificada depende de autorização específica. Sem essa autorização, utilizar uma versão anonimizada e dados fictícios ou devidamente anonimizados.

