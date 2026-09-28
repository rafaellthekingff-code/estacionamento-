"""
Menus de navegação do sistema (interface de terminal) e função
`main()` que orquestra a aplicação, com tratamento de exceções
para garantir que os dados sejam sempre salvos ao encerrar.
"""

from . import config
from . import persistencia
from . import vagas
from . import clientes
from . import veiculos
from . import registros
from . import relatorios
from .validacao import limpar_tela, ler_opcao


def menu_vagas():
    while True:
        limpar_tela()
        print("=== GESTÃO DE VAGAS ===\n")
        print("1. Cadastrar vaga")
        print("2. Listar vagas")
        print("3. Atualizar / Interditar vaga")
        print("4. Remover vaga")
        print("0. Voltar ao menu principal")
        opcao = ler_opcao("\nEscolha uma opção: ", ["0", "1", "2", "3", "4"])
        if opcao == "1":
            vagas.criar_vaga()
        elif opcao == "2":
            vagas.listar_vagas()
        elif opcao == "3":
            vagas.atualizar_vaga()
        elif opcao == "4":
            vagas.deletar_vaga()
        elif opcao == "0":
            break


def menu_clientes():
    while True:
        limpar_tela()
        print("=== GESTÃO DE CLIENTES / MENSALISTAS ===\n")
        print("1. Cadastrar cliente")
        print("2. Listar clientes")
        print("3. Atualizar cliente / registrar pagamento")
        print("4. Remover cliente")
        print("0. Voltar ao menu principal")
        opcao = ler_opcao("\nEscolha uma opção: ", ["0", "1", "2", "3", "4"])
        if opcao == "1":
            clientes.criar_cliente()
        elif opcao == "2":
            clientes.listar_clientes()
        elif opcao == "3":
            clientes.atualizar_cliente()
        elif opcao == "4":
            clientes.deletar_cliente()
        elif opcao == "0":
            break


def menu_veiculos():
    while True:
        limpar_tela()
        print("=== GESTÃO DE VEÍCULOS ===\n")
        print("1. Cadastrar veículo")
        print("2. Listar veículos")
        print("3. Atualizar veículo")
        print("4. Remover veículo")
        print("0. Voltar ao menu principal")
        opcao = ler_opcao("\nEscolha uma opção: ", ["0", "1", "2", "3", "4"])
        if opcao == "1":
            veiculos.criar_veiculo()
        elif opcao == "2":
            veiculos.listar_veiculos()
        elif opcao == "3":
            veiculos.atualizar_veiculo()
        elif opcao == "4":
            veiculos.deletar_veiculo()
        elif opcao == "0":
            break


def menu_operacoes():
    while True:
        limpar_tela()
        print("=== OPERAÇÕES DO ESTACIONAMENTO ===\n")
        print("1. Registrar entrada de veículo")
        print("2. Registrar saída de veículo")
        print("3. Ver veículos estacionados agora")
        print("0. Voltar ao menu principal")
        opcao = ler_opcao("\nEscolha uma opção: ", ["0", "1", "2", "3"])
        if opcao == "1":
            registros.registrar_entrada()
        elif opcao == "2":
            registros.registrar_saida()
        elif opcao == "3":
            registros.listar_registros_abertos()
        elif opcao == "0":
            break


def menu_relatorios():
    while True:
        limpar_tela()
        print("=== RELATÓRIOS ===\n")
        print("1. Ocupação atual do estacionamento")
        print("2. Faturamento por período")
        print("3. Histórico por veículo (placa)")
        print("0. Voltar ao menu principal")
        opcao = ler_opcao("\nEscolha uma opção: ", ["0", "1", "2", "3"])
        if opcao == "1":
            relatorios.relatorio_ocupacao()
        elif opcao == "2":
            relatorios.relatorio_faturamento_periodo()
        elif opcao == "3":
            relatorios.relatorio_historico_veiculo()
        elif opcao == "0":
            break


def menu_principal():
    while True:
        limpar_tela()
        print("╔══════════════════════════════════════════════╗")
        print("║   SISTEMA DE GESTÃO DE ESTACIONAMENTO         ║")
        print("╚══════════════════════════════════════════════╝\n")
        print("1. Gestão de Vagas")
        print("2. Gestão de Clientes / Mensalistas")
        print("3. Gestão de Veículos")
        print("4. Operações (Entrada / Saída)")
        print("5. Relatórios")
        print("0. Sair")
        opcao = ler_opcao("\nEscolha uma opção: ", ["0", "1", "2", "3", "4", "5"])
        if opcao == "1":
            menu_vagas()
        elif opcao == "2":
            menu_clientes()
        elif opcao == "3":
            menu_veiculos()
        elif opcao == "4":
            menu_operacoes()
        elif opcao == "5":
            menu_relatorios()
        elif opcao == "0":
            print("\nEncerrando o sistema... Dados salvos com sucesso. Até logo!")
            break


def salvar_tudo():
    """Persiste o estado atual de todas as entidades em disco."""
    persistencia.salvar_dados(config.ARQ_VAGAS, vagas.vagas)
    persistencia.salvar_dados(config.ARQ_CLIENTES, clientes.clientes)
    persistencia.salvar_dados(config.ARQ_VEICULOS, veiculos.veiculos)
    persistencia.salvar_dados(config.ARQ_REGISTROS, registros.registros)


def main():
    try:
        menu_principal()
        salvar_tudo()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário. Salvando dados antes de sair...")
        salvar_tudo()
    except Exception as erro:  # tratamento genérico para não perder dados em caso de falha
        print(f"\n[Erro inesperado] {erro}")
        print("Salvando dados antes de encerrar...")
        salvar_tudo()
