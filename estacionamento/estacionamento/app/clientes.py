"""
Módulo de gestão de Clientes: CRUD completo, incluindo os dois
perfis de cliente (Avulso e Mensalista) e a verificação de
mensalidade em dia.
"""

from datetime import datetime, timedelta

from . import config
from . import persistencia
from .validacao import (
    limpar_tela, pausar, ler_texto, ler_inteiro,
    ler_opcao_lista, ler_sim_nao, proximo_id,
)

# Estado em memória do módulo, carregado do disco na importação
clientes = persistencia.carregar_dados(config.ARQ_CLIENTES)


def criar_cliente():
    limpar_tela()
    print("=== CADASTRAR NOVO CLIENTE ===\n")
    nome = ler_texto("Nome completo: ")
    cpf = ler_texto("CPF (apenas números): ")
    if any(c["cpf"] == cpf for c in clientes):
        print("⚠ Já existe um cliente com esse CPF.")
        pausar()
        return
    telefone = ler_texto("Telefone: ")

    print("\nTipo de cliente:")
    tipo = ler_opcao_lista("Escolha o tipo: ", config.TIPOS_CLIENTE)

    cliente = {
        "id": proximo_id(clientes),
        "nome": nome,
        "cpf": cpf,
        "telefone": telefone,
        "tipo": tipo,
        "data_validade_mensalidade": None,
    }
    if tipo == "Mensalista":
        validade = datetime.now() + timedelta(days=config.DIAS_VALIDADE_MENSALIDADE)
        cliente["data_validade_mensalidade"] = validade.strftime("%Y-%m-%d")
        print(f"\nMensalidade registrada como paga até {validade.strftime('%d/%m/%Y')}.")

    clientes.append(cliente)
    persistencia.salvar_dados(config.ARQ_CLIENTES, clientes)
    print(f"\n✅ Cliente {nome} cadastrado com sucesso! (ID: {cliente['id']})")
    pausar()


def mensalidade_em_dia(cliente):
    """Verifica se a mensalidade do cliente está em dia (regra de negócio)."""
    if cliente["tipo"] != "Mensalista" or not cliente.get("data_validade_mensalidade"):
        return False
    validade = datetime.strptime(cliente["data_validade_mensalidade"], "%Y-%m-%d")
    return datetime.now().date() <= validade.date()


def listar_clientes(mostrar_pausa=True):
    limpar_tela()
    print("=== LISTA DE CLIENTES ===\n")
    if not clientes:
        print("Nenhum cliente cadastrado.")
    else:
        print(f"{'ID':<4}{'Nome':<22}{'CPF':<15}{'Tipo':<12}{'Situação':<12}")
        print("-" * 65)
        for c in clientes:
            situacao = "-"
            if c["tipo"] == "Mensalista":
                situacao = "Em dia" if mensalidade_em_dia(c) else "Atrasada"
            print(f"{c['id']:<4}{c['nome']:<22}{c['cpf']:<15}{c['tipo']:<12}{situacao:<12}")
    if mostrar_pausa:
        pausar()


def buscar_cliente_por_id(id_cliente):
    return next((c for c in clientes if c["id"] == id_cliente), None)


def atualizar_cliente():
    listar_clientes(mostrar_pausa=False)
    if not clientes:
        pausar()
        return
    id_cliente = ler_inteiro("\nDigite o ID do cliente que deseja atualizar (0 para cancelar): ", 0)
    if id_cliente == 0:
        return
    cliente = buscar_cliente_por_id(id_cliente)
    if not cliente:
        print("⚠ Cliente não encontrado.")
        pausar()
        return

    print(f"\nEditando cliente {cliente['nome']}")
    novo_nome = ler_texto(f"Nome [{cliente['nome']}] (ENTER mantém): ", obrigatorio=False)
    if novo_nome:
        cliente["nome"] = novo_nome
    novo_telefone = ler_texto(f"Telefone [{cliente['telefone']}] (ENTER mantém): ", obrigatorio=False)
    if novo_telefone:
        cliente["telefone"] = novo_telefone

    if cliente["tipo"] == "Mensalista" and ler_sim_nao("Deseja registrar o pagamento da mensalidade?"):
        validade = datetime.now() + timedelta(days=config.DIAS_VALIDADE_MENSALIDADE)
        cliente["data_validade_mensalidade"] = validade.strftime("%Y-%m-%d")
        print(f"Mensalidade paga até {validade.strftime('%d/%m/%Y')}.")

    persistencia.salvar_dados(config.ARQ_CLIENTES, clientes)
    print("\n✅ Cliente atualizado com sucesso!")
    pausar()


def deletar_cliente():
    listar_clientes(mostrar_pausa=False)
    if not clientes:
        pausar()
        return
    id_cliente = ler_inteiro("\nDigite o ID do cliente que deseja remover (0 para cancelar): ", 0)
    if id_cliente == 0:
        return
    cliente = buscar_cliente_por_id(id_cliente)
    if not cliente:
        print("⚠ Cliente não encontrado.")
        pausar()
        return

    # Import tardio (dentro da função) para evitar import circular,
    # já que veiculos.py também importa este módulo no nível superior.
    from . import veiculos as veiculos_mod
    if any(v["cliente_id"] == id_cliente for v in veiculos_mod.veiculos):
        print("⚠ Não é possível remover: existem veículos vinculados a este cliente.")
        pausar()
        return

    if ler_sim_nao(f"Confirma a remoção do cliente {cliente['nome']}?"):
        clientes.remove(cliente)
        persistencia.salvar_dados(config.ARQ_CLIENTES, clientes)
        print("✅ Cliente removido com sucesso!")
    pausar()
