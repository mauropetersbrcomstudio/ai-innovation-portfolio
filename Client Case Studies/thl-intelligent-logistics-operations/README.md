# Intelligent Logistics Operations — THL

**Status:** MVP inicial em desenvolvimento  
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
- Registra ocorrências operacionais.
- Mantém histórico local de eventos e permite exportar os dados em JSON.
- Exibe uma visão geral baseada exclusivamente nos registros inseridos.

## O que esta versão não faz

- Não conecta a ERP, TMS, WMS, transportadoras, rastreadores, e-mail, WhatsApp ou BI.
- Não consulta dados externos nem transmite informações.
- Não emite NF-e, CT-e ou MDF-e.
- Não contrata fretes, despacha veículos, movimenta estoque físico ou confirma entregas.
- Não possui autenticação multiusuário nem banco de dados central.
- Não utiliza modelo externo de IA. As classificações e registros são manuais nesta primeira versão.

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

## Próximas etapas

1. Validar os campos de coleta com a equipe THL.
2. Completar regras operacionais e estados de cada modalidade.
3. Implementar gestão de ocorrências e documentos com critérios validados.
4. Definir modelo de persistência e autenticação antes de qualquer uso compartilhado.
5. Planejar agentes de IA após a qualidade e os formatos dos dados serem avaliados.

## Integridade do case

A confirmação do fluxo operacional não representa confirmação de indicadores, volumes, sistemas utilizados, regras internas, resultados ou autorização para publicação pública do nome e logotipo. Esses itens precisam de evidência ou autorização específica.
