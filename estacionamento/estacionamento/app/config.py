"""
Configurações e constantes globais do sistema de estacionamento.
Centralizar esses valores aqui facilita ajustar regras de negócio
(tarifas, tolerância, caminhos de arquivo) sem mexer na lógica.
"""

import os

# ---------------------------------------------------------------
# Caminhos de persistência (arquivos .txt em formato JSON)
# ---------------------------------------------------------------
DIRETORIO_DADOS = "dados_estacionamento"
ARQ_VAGAS = os.path.join(DIRETORIO_DADOS, "vagas.txt")
ARQ_CLIENTES = os.path.join(DIRETORIO_DADOS, "clientes.txt")
ARQ_VEICULOS = os.path.join(DIRETORIO_DADOS, "veiculos.txt")
ARQ_REGISTROS = os.path.join(DIRETORIO_DADOS, "registros.txt")

# ---------------------------------------------------------------
# Domínios válidos (usados nas validações e menus)
# ---------------------------------------------------------------
TIPOS_COBERTURA = ["Coberta", "Descoberta"]
TIPOS_VAGA = ["Comum", "Preferencial", "Moto"]
TIPOS_CLIENTE = ["Avulso", "Mensalista"]
TIPOS_VEICULO = ["Carro", "Moto"]

# ---------------------------------------------------------------
# Regras de tarifação
# ---------------------------------------------------------------
TARIFA_HORA_DIURNA = 6.00       # R$ por hora no período diurno
TARIFA_HORA_NOTURNA = 4.00      # R$ por hora no período noturno
INICIO_DIURNO = 6                # 06:00
INICIO_NOTURNO = 22               # 22:00
TOLERANCIA_MINUTOS = 10           # minutos de tolerância sem cobrança
TAXA_PERDA_TICKET = 50.00         # taxa fixa por perda do ticket
DIAS_VALIDADE_MENSALIDADE = 30    # validade padrão da mensalidade em dias
