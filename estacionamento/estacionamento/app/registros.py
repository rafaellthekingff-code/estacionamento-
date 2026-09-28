"""
Módulo de Registros de Entrada/Saída: aplica as regras de negócio
centrais do estacionamento — atribuição de vaga na entrada, cálculo
de tarifas na saída (avulso x mensalista) e liberação da vaga.
"""

import math
from datetime import datetime

from . import config
from . import persistencia
from . import vagas as vagas_mod
from . import veiculos as veiculos_mod
from . import clientes as clientes_mod
from .validacao import limpar_tela, pausar, ler_placa, ler_sim_nao, proximo_id

# Estado em memória do módulo, carregado do disco na importação
registros = persistencia.carregar_dados(config.ARQ_REGISTROS)


def calcular_valor_avulso(hora_entrada, hora_saida):
    """Calcula o valor cobrado de um cliente avulso, considerando:
       - tolerância inicial sem cobrança;
       - tarifa diferenciada para período diurno/noturno (com base no
         horário de saída);
       - cobrança por hora cheia + fração (cada fração de até 30 min
         iniciada é cobrada como meia hora)."""
    minutos = (hora_saida - hora_entrada).total_seconds() / 60
    if minutos <= config.TOLERANCIA_MINUTOS:
        return 0.0

    periodo_noturno = hora_saida.hour >= config.INICIO_NOTURNO or hora_saida.hour < config.INICIO_DIURNO
    tarifa_hora = config.TARIFA_HORA_NOTURNA if periodo_noturno else config.TARIFA_HORA_DIURNA

    horas_completas = int(minutos // 60)
    minutos_restantes = minutos % 60

    valor = horas_completas * tarifa_hora
    if minutos_restantes > 0:
        fracoes = math.ceil(minutos_restantes / 30)
        valor += fracoes * (tarifa_hora / 2)

    return round(valor, 2)


def registrar_entrada():
    limpar_tela()
    print("=== REGISTRAR ENTRADA DE VEÍCULO ===\n")
    placa = ler_placa("Placa do veículo: ")

    if any(r["placa"] == placa and r["status"] == "Aberto" for r in registros):
        print("⚠ Este veículo já possui uma entrada em aberto no estacionamento.")
        pausar()
        return

    veiculo = veiculos_mod.buscar_veiculo_por_placa(placa)
    if not veiculo:
        print("\nVeículo não cadastrado. Vamos realizar um cadastro rápido.")
        from .validacao import ler_texto, ler_opcao_lista
        modelo = ler_texto("Modelo/Marca: ")
        tipo = ler_opcao_lista("Tipo de veículo: ", config.TIPOS_VEICULO)
        veiculo = {"id": proximo_id(veiculos_mod.veiculos), "placa": placa, "modelo": modelo, "tipo": tipo, "cliente_id": None}
        veiculos_mod.veiculos.append(veiculo)
        persistencia.salvar_dados(config.ARQ_VEICULOS, veiculos_mod.veiculos)

    cliente = clientes_mod.buscar_cliente_por_id(veiculo["cliente_id"]) if veiculo["cliente_id"] else None
    if cliente and cliente["tipo"] == "Mensalista":
        if not clientes_mod.mensalidade_em_dia(cliente):
            print(f"\n⚠ O cliente {cliente['nome']} está com a mensalidade ATRASADA.")
            if not ler_sim_nao("Deseja permitir a entrada mesmo assim (cobrança avulsa na saída)?"):
                print("Entrada cancelada.")
                pausar()
                return
        else:
            print(f"\nCliente mensalista {cliente['nome']} identificado — mensalidade em dia.")

    vaga = vagas_mod.buscar_vaga_livre_compativel(veiculo["tipo"])
    if not vaga:
        print(f"\n⚠ Não há vagas disponíveis compatíveis com o tipo '{veiculo['tipo']}' no momento.")
        pausar()
        return

    agora = datetime.now()
    registro = {
        "id": proximo_id(registros),
        "placa": placa,
        "vaga_id": vaga["id"],
        "hora_entrada": agora.isoformat(),
        "hora_saida": None,
        "valor": None,
        "perdeu_ticket": False,
        "status": "Aberto",
    }
    registros.append(registro)
    vaga["status"] = "Ocupada"
    persistencia.salvar_dados(config.ARQ_REGISTROS, registros)
    persistencia.salvar_dados(config.ARQ_VAGAS, vagas_mod.vagas)

    print(f"\n✅ Entrada registrada às {agora.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Vaga atribuída: {vaga['identificacao']} ({vaga['tipo']} / {vaga['cobertura']})")
    print(f"   Ticket nº {registro['id']} — guarde este número para a saída.")
    pausar()


def registrar_saida():
    limpar_tela()
    print("=== REGISTRAR SAÍDA DE VEÍCULO ===\n")
    placa = ler_placa("Placa do veículo: ")

    registro = next((r for r in registros if r["placa"] == placa and r["status"] == "Aberto"), None)
    if not registro:
        print("⚠ Nenhuma entrada em aberto encontrada para esta placa.")
        pausar()
        return

    hora_entrada = datetime.fromisoformat(registro["hora_entrada"])
    hora_saida = datetime.now()
    vaga = vagas_mod.buscar_vaga_por_id(registro["vaga_id"])
    veiculo = veiculos_mod.buscar_veiculo_por_placa(placa)
    cliente = clientes_mod.buscar_cliente_por_id(veiculo["cliente_id"]) if veiculo and veiculo["cliente_id"] else None

    perdeu_ticket = ler_sim_nao("O cliente perdeu o ticket de entrada?")

    if perdeu_ticket:
        valor = config.TAXA_PERDA_TICKET
        print(f"\nSerá cobrada a taxa fixa de perda de ticket: R$ {valor:.2f}")
    elif cliente and cliente["tipo"] == "Mensalista" and clientes_mod.mensalidade_em_dia(cliente):
        valor = 0.0
        print("\nCliente mensalista em dia — sem cobrança adicional.")
    else:
        valor = calcular_valor_avulso(hora_entrada, hora_saida)

    registro["hora_saida"] = hora_saida.isoformat()
    registro["valor"] = valor
    registro["perdeu_ticket"] = perdeu_ticket
    registro["status"] = "Fechado"

    if vaga:
        vaga["status"] = "Interditada" if vaga["interditada"] else "Livre"

    persistencia.salvar_dados(config.ARQ_REGISTROS, registros)
    persistencia.salvar_dados(config.ARQ_VAGAS, vagas_mod.vagas)

    permanencia = hora_saida - hora_entrada
    horas, resto = divmod(int(permanencia.total_seconds()), 3600)
    minutos = resto // 60

    print("\n----- COMPROVANTE DE SAÍDA -----")
    print(f"Placa: {placa}")
    print(f"Entrada: {hora_entrada.strftime('%d/%m/%Y %H:%M')}")
    print(f"Saída:   {hora_saida.strftime('%d/%m/%Y %H:%M')}")
    print(f"Permanência: {horas}h{minutos:02d}min")
    print(f"Valor cobrado: R$ {valor:.2f}")
    print("---------------------------------")
    pausar()


def listar_registros_abertos(mostrar_pausa=True):
    limpar_tela()
    print("=== VEÍCULOS ATUALMENTE NO ESTACIONAMENTO ===\n")
    abertos = [r for r in registros if r["status"] == "Aberto"]
    if not abertos:
        print("Nenhum veículo estacionado no momento.")
    else:
        print(f"{'Ticket':<8}{'Placa':<10}{'Vaga':<8}{'Entrada':<18}")
        print("-" * 50)
        for r in abertos:
            vaga = vagas_mod.buscar_vaga_por_id(r["vaga_id"])
            entrada = datetime.fromisoformat(r["hora_entrada"]).strftime("%d/%m %H:%M")
            print(f"{r['id']:<8}{r['placa']:<10}{vaga['identificacao'] if vaga else '-':<8}{entrada:<18}")
    if mostrar_pausa:
        pausar()
