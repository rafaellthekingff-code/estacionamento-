# Sistema de Gestão de Estacionamento

Sistema de terminal em Python 3 (sem dependências externas) para
gerenciar vagas, clientes/mensalistas, veículos e o fluxo de
entrada/saída de um estacionamento.

## Estrutura de pastas

```
estacionamento/
├── main.py                 # ponto de entrada (execute este arquivo)
├── README.md
├── app/
│   ├── __init__.py
│   ├── config.py            # constantes e regras de tarifação
│   ├── persistencia.py      # leitura/gravação dos arquivos .txt
│   ├── validacao.py         # validação de entrada e utilidades de terminal
│   ├── vagas.py              # CRUD de vagas + vaga compatível
│   ├── clientes.py           # CRUD de clientes (Avulso/Mensalista)
│   ├── veiculos.py           # CRUD de veículos
│   ├── registros.py          # entrada/saída e cálculo de tarifas
│   ├── relatorios.py         # relatórios com filtros
│   └── menus.py              # menus de terminal e função main()
└── dados_estacionamento/     # criada automaticamente na 1ª execução
    ├── vagas.txt
    ├── clientes.txt
    ├── veiculos.txt
    └── registros.txt
```

## Como executar

```bash
cd estacionamento
python3 main.py
```

Não é necessário instalar nada: o projeto usa apenas módulos nativos
do Python (`os`, `json`, `math`, `datetime`).

## Fluxo recomendado de uso

1. Menu **1 — Gestão de Vagas**: cadastre algumas vagas antes de
   registrar qualquer entrada (senão não haverá vaga disponível).
2. Menu **2 — Gestão de Clientes**: cadastre mensalistas, se desejar
   vincular veículos a eles.
3. Menu **3 — Gestão de Veículos**: cadastre veículos (opcionalmente
   vinculados a um cliente).
4. Menu **4 — Operações**: registre entradas e saídas. A vaga
   compatível é atribuída automaticamente.
5. Menu **5 — Relatórios**: consulte ocupação atual, faturamento por
   período e histórico por placa.

## Regras de negócio implementadas

- **Vagas**: tipos de cobertura (Coberta/Descoberta), tipos de vaga
  (Comum/Preferencial/Moto) e controle de interdição.
- **Atribuição automática**: motos só ocupam vagas de moto; carros
  priorizam vagas comuns e usam preferenciais como alternativa.
- **Cliente Avulso**: cobrança por tempo de permanência, com
  tolerância inicial, tarifa diurna/noturna diferenciada, cobrança
  por hora cheia + fração e taxa fixa por perda de ticket.
- **Cliente Mensalista**: vínculo fixo ao veículo e verificação
  automática de mensalidade em dia na entrada e na saída.

## Persistência

Os dados são gravados automaticamente em arquivos `.txt` (formato
JSON) dentro da pasta `dados_estacionamento/`, que é criada
automaticamente. Eles são recarregados a cada nova execução do
programa.
