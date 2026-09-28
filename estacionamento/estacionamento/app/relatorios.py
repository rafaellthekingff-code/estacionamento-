"""
Módulo de Relatórios: consultas com filtros sobre os dados do
estacionamento (ocupação atual, faturamento por período e
histórico por veículo).
"""

from datetime import datetime

from . import config
from . import vagas as vagas_mod
from . import registros as registros_mod
from .validacao import limpar_tela, pausar, ler_data, ler_placa


def relatorio_ocupacao():
    limpar_tela()
    print("=== RELATÓRIO DE OCUPAÇÃO ATUAL ===\n")
    if not vagas_mod.vagas:
        print("Nenhuma vaga cadastrada.")
        pausar()
        return

    total = len(vagas_mod.vagas)
    livres = sum(1 for v in vagas_mod.vagas if v["status"] == "Livre")
    ocupadas = sum(1 for v in vagas_mod.vagas if v["status"] == "Ocupada")
    interditadas = sum(1 for v in vagas_mod.vagas if v["status"] == "Interditada")

    print(f"Total de vagas:     {total}")
    print(f"  Livres:           {livres}")
    print(f"  Ocupadas:         {ocupadas}")
    print(f"  Interditadas:     {interditadas}")
    print(f"  Taxa de ocupação: {ocupadas / total * 100:.1f}%\n")

    print("Detalhamento por tipo de vaga:")
    for tipo in config.TIPOS_VAGA:
        do_tipo = [v for v in vagas_mod.vagas if v["tipo"] == tipo]
        if do_tipo:
            livres_tipo = sum(1 for v in do_tipo if v["status"] == "Livre")
            print(f"  {tipo:<14}: {livres_tipo}/{len(do_tipo)} livres")
    pausar()


def relatorio_faturamento_periodo():
    limpar_tela()
    print("=== RELATÓRIO DE FATURAMENTO POR PERÍODO ===\n")
    print("Informe o período de consulta:")
    data_inicio = ler_data("Data inicial (DD/MM/AAAA): ")
    data_fim = ler_data("Data final (DD/MM/AAAA): ")

    if data_fim < data_inicio:
        print("⚠ A data final não pode ser anterior à data inicial.")
        pausar()
        return

    fim_do_dia = data_fim.replace(hour=23, minute=59, second=59)
    fechados = [
        r for r in registros_mod.registros
        if r["status"] == "Fechado" and data_inicio <= datetime.fromisoformat(r["hora_saida"]) <= fim_do_dia
    ]

    if not fechados:
        print("\nNenhum registro de saída encontrado no período informado.")
        pausar()
        return

    total = sum(r["valor"] for r in fechados)
    qtd_perda_ticket = sum(1 for r in fechados if r["perdeu_ticket"])

    print(f"\nPeríodo: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    print(f"Total de veículos atendidos: {len(fechados)}")
    print(f"Ocorrências de perda de ticket: {qtd_perda_ticket}")
    print(f"Faturamento total: R$ {total:.2f}")
    print(f"Ticket médio: R$ {total / len(fechados):.2f}")
    pausar()


def relatorio_historico_veiculo():
    limpar_tela()
    print("=== HISTÓRICO POR VEÍCULO ===\n")
    placa = ler_placa("Digite a placa do veículo: ")
    historico = [r for r in registros_mod.registros if r["placa"] == placa]

    if not historico:
        print("Nenhum registro encontrado para esta placa.")
        pausar()
        return

    print(f"\n{'Ticket':<8}{'Entrada':<18}{'Saída':<18}{'Valor':<12}{'Situação':<10}")
    print("-" * 66)
    for r in historico:
        entrada = datetime.fromisoformat(r["hora_entrada"]).strftime("%d/%m %H:%M")
        saida = datetime.fromisoformat(r["hora_saida"]).strftime("%d/%m %H:%M") if r["hora_saida"] else "-"
        valor = f"R$ {r['valor']:.2f}" if r["valor"] is not None else "-"
        print(f"{r['id']:<8}{entrada:<18}{saida:<18}{valor:<12}{r['status']:<10}")
    pausar()
