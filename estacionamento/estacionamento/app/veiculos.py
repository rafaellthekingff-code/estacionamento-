"""
Módulo de gestão de Veículos: CRUD completo, incluindo o vínculo
opcional com um cliente já cadastrado (usado para identificar
mensalistas automaticamente na entrada/saída).
"""

from . import config
from . import persistencia
from . import clientes as clientes_mod
from .validacao import (
    limpar_tela, pausar, ler_texto, ler_inteiro,
    ler_opcao_lista, ler_sim_nao, ler_placa, proximo_id,
)

# Estado em memória do módulo, carregado do disco na importação
veiculos = persistencia.carregar_dados(config.ARQ_VEICULOS)


def buscar_veiculo_por_placa(placa):
    placa = placa.upper()
    return next((v for v in veiculos if v["placa"] == placa), None)


def buscar_veiculo_por_id(id_veiculo):
    return next((v for v in veiculos if v["id"] == id_veiculo), None)


def criar_veiculo():
    limpar_tela()
    print("=== CADASTRAR NOVO VEÍCULO ===\n")
    placa = ler_placa("Placa do veículo: ")
    if buscar_veiculo_por_placa(placa):
        print("⚠ Já existe um veículo cadastrado com essa placa.")
        pausar()
        return
    modelo = ler_texto("Modelo/Marca: ")
    print("\nTipo de veículo:")
    tipo = ler_opcao_lista("Escolha o tipo: ", config.TIPOS_VEICULO)

    cliente_id = None
    if ler_sim_nao("Deseja vincular este veículo a um cliente cadastrado?"):
        clientes_mod.listar_clientes(mostrar_pausa=False)
        if clientes_mod.clientes:
            id_c = ler_inteiro("Digite o ID do cliente (0 para não vincular): ", 0)
            if id_c != 0:
                cliente = clientes_mod.buscar_cliente_por_id(id_c)
                if cliente:
                    cliente_id = cliente["id"]
                else:
                    print("⚠ Cliente não encontrado. Veículo cadastrado sem vínculo.")
        else:
            print("Nenhum cliente cadastrado ainda.")

    veiculo = {
        "id": proximo_id(veiculos),
        "placa": placa,
        "modelo": modelo,
        "tipo": tipo,
        "cliente_id": cliente_id,
    }
    veiculos.append(veiculo)
    persistencia.salvar_dados(config.ARQ_VEICULOS, veiculos)
    print(f"\n✅ Veículo {placa} cadastrado com sucesso!")
    pausar()


def listar_veiculos(mostrar_pausa=True):
    limpar_tela()
    print("=== LISTA DE VEÍCULOS ===\n")
    if not veiculos:
        print("Nenhum veículo cadastrado.")
    else:
        print(f"{'ID':<4}{'Placa':<10}{'Modelo':<16}{'Tipo':<8}{'Cliente':<20}")
        print("-" * 60)
        for v in veiculos:
            nome_cliente = "-"
            if v["cliente_id"]:
                cli = clientes_mod.buscar_cliente_por_id(v["cliente_id"])
                nome_cliente = cli["nome"] if cli else "-"
            print(f"{v['id']:<4}{v['placa']:<10}{v['modelo']:<16}{v['tipo']:<8}{nome_cliente:<20}")
    if mostrar_pausa:
        pausar()


def atualizar_veiculo():
    listar_veiculos(mostrar_pausa=False)
    if not veiculos:
        pausar()
        return
    id_v = ler_inteiro("\nDigite o ID do veículo que deseja atualizar (0 para cancelar): ", 0)
    if id_v == 0:
        return
    veiculo = buscar_veiculo_por_id(id_v)
    if not veiculo:
        print("⚠ Veículo não encontrado.")
        pausar()
        return

    novo_modelo = ler_texto(f"Modelo [{veiculo['modelo']}] (ENTER mantém): ", obrigatorio=False)
    if novo_modelo:
        veiculo["modelo"] = novo_modelo
    if ler_sim_nao("Deseja alterar o tipo do veículo?"):
        veiculo["tipo"] = ler_opcao_lista("Novo tipo: ", config.TIPOS_VEICULO)
    if ler_sim_nao("Deseja alterar o vínculo com cliente?"):
        if ler_sim_nao("Deseja remover o vínculo atual?"):
            veiculo["cliente_id"] = None
        else:
            clientes_mod.listar_clientes(mostrar_pausa=False)
            if clientes_mod.clientes:
                id_c = ler_inteiro("Digite o ID do novo cliente (0 para cancelar): ", 0)
                if id_c != 0:
                    cliente = clientes_mod.buscar_cliente_por_id(id_c)
                    if cliente:
                        veiculo["cliente_id"] = cliente["id"]
                    else:
                        print("⚠ Cliente não encontrado.")

    persistencia.salvar_dados(config.ARQ_VEICULOS, veiculos)
    print("\n✅ Veículo atualizado com sucesso!")
    pausar()


def deletar_veiculo():
    listar_veiculos(mostrar_pausa=False)
    if not veiculos:
        pausar()
        return
    id_v = ler_inteiro("\nDigite o ID do veículo que deseja remover (0 para cancelar): ", 0)
    if id_v == 0:
        return
    veiculo = buscar_veiculo_por_id(id_v)
    if not veiculo:
        print("⚠ Veículo não encontrado.")
        pausar()
        return

    # Import tardio para evitar import circular (registros.py também
    # importa este módulo no nível superior).
    from . import registros as registros_mod
    if any(r["placa"] == veiculo["placa"] and r["status"] == "Aberto" for r in registros_mod.registros):
        print("⚠ Não é possível remover: veículo está atualmente estacionado.")
        pausar()
        return

    if ler_sim_nao(f"Confirma a remoção do veículo {veiculo['placa']}?"):
        veiculos.remove(veiculo)
        persistencia.salvar_dados(config.ARQ_VEICULOS, veiculos)
        print("✅ Veículo removido com sucesso!")
    pausar()
