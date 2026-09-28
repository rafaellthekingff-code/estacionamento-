"""
Módulo de gestão de Vagas: CRUD completo e a regra de negócio de
atribuição automática de vaga compatível com o tipo de veículo.
"""

from . import config
from . import persistencia
from .validacao import (
    limpar_tela, pausar, ler_texto, ler_inteiro,
    ler_opcao_lista, ler_sim_nao, proximo_id,
)

# Estado em memória do módulo, carregado do disco na importação
vagas = persistencia.carregar_dados(config.ARQ_VAGAS)


def criar_vaga():
    limpar_tela()
    print("=== CADASTRAR NOVA VAGA ===\n")
    identificacao = ler_texto("Identificação da vaga (ex: A01): ").upper()
    if any(v["identificacao"] == identificacao for v in vagas):
        print("⚠ Já existe uma vaga com essa identificação.")
        pausar()
        return

    print("\nTipo de cobertura:")
    cobertura = ler_opcao_lista("Escolha o tipo de cobertura: ", config.TIPOS_COBERTURA)
    print("\nTipo de vaga:")
    tipo = ler_opcao_lista("Escolha o tipo de vaga: ", config.TIPOS_VAGA)

    vaga = {
        "id": proximo_id(vagas),
        "identificacao": identificacao,
        "cobertura": cobertura,
        "tipo": tipo,
        "status": "Livre",
        "interditada": False,
        "motivo_interdicao": None,
    }
    vagas.append(vaga)
    persistencia.salvar_dados(config.ARQ_VAGAS, vagas)
    print(f"\n✅ Vaga {identificacao} cadastrada com sucesso!")
    pausar()


def listar_vagas(mostrar_pausa=True):
    limpar_tela()
    print("=== LISTA DE VAGAS ===\n")
    if not vagas:
        print("Nenhuma vaga cadastrada.")
    else:
        print(f"{'ID':<4}{'Identificação':<15}{'Cobertura':<12}{'Tipo':<14}{'Status':<14}")
        print("-" * 60)
        for v in sorted(vagas, key=lambda x: x["identificacao"]):
            print(f"{v['id']:<4}{v['identificacao']:<15}{v['cobertura']:<12}{v['tipo']:<14}{v['status']:<14}")
    if mostrar_pausa:
        pausar()


def buscar_vaga_por_id(id_vaga):
    return next((v for v in vagas if v["id"] == id_vaga), None)


def atualizar_vaga():
    listar_vagas(mostrar_pausa=False)
    if not vagas:
        pausar()
        return
    id_vaga = ler_inteiro("\nDigite o ID da vaga que deseja atualizar (0 para cancelar): ", 0)
    if id_vaga == 0:
        return
    vaga = buscar_vaga_por_id(id_vaga)
    if not vaga:
        print("⚠ Vaga não encontrada.")
        pausar()
        return

    print(f"\nEditando vaga {vaga['identificacao']}")
    nova_identificacao = ler_texto(f"Nova identificação [{vaga['identificacao']}] (ENTER mantém): ", obrigatorio=False)
    if nova_identificacao:
        vaga["identificacao"] = nova_identificacao.upper()
    if ler_sim_nao("Deseja alterar o tipo de cobertura?"):
        vaga["cobertura"] = ler_opcao_lista("Novo tipo de cobertura: ", config.TIPOS_COBERTURA)
    if ler_sim_nao("Deseja alterar o tipo da vaga?"):
        vaga["tipo"] = ler_opcao_lista("Novo tipo de vaga: ", config.TIPOS_VAGA)
    if ler_sim_nao("Deseja alterar a interdição da vaga?"):
        if vaga["interditada"]:
            vaga["interditada"] = False
            vaga["motivo_interdicao"] = None
            vaga["status"] = "Livre"
            print("Interdição removida. Vaga liberada.")
        else:
            if vaga["status"] == "Ocupada":
                print("⚠ Não é possível interditar uma vaga ocupada.")
            else:
                motivo = ler_texto("Motivo da interdição: ")
                vaga["interditada"] = True
                vaga["motivo_interdicao"] = motivo
                vaga["status"] = "Interditada"
                print("Vaga interditada com sucesso.")

    persistencia.salvar_dados(config.ARQ_VAGAS, vagas)
    print("\n✅ Vaga atualizada com sucesso!")
    pausar()


def deletar_vaga():
    listar_vagas(mostrar_pausa=False)
    if not vagas:
        pausar()
        return
    id_vaga = ler_inteiro("\nDigite o ID da vaga que deseja remover (0 para cancelar): ", 0)
    if id_vaga == 0:
        return
    vaga = buscar_vaga_por_id(id_vaga)
    if not vaga:
        print("⚠ Vaga não encontrada.")
        pausar()
        return
    if vaga["status"] == "Ocupada":
        print("⚠ Não é possível remover uma vaga ocupada.")
        pausar()
        return
    if ler_sim_nao(f"Confirma a remoção da vaga {vaga['identificacao']}?"):
        vagas.remove(vaga)
        persistencia.salvar_dados(config.ARQ_VAGAS, vagas)
        print("✅ Vaga removida com sucesso!")
    pausar()


def buscar_vaga_livre_compativel(tipo_veiculo):
    """Regra de negócio: atribuição automática de vaga compatível.
    Motos só ocupam vagas do tipo 'Moto'. Carros priorizam vagas
    'Comum' e, na ausência destas, utilizam vagas 'Preferencial'."""
    if tipo_veiculo == "Moto":
        candidatas = [v for v in vagas if v["tipo"] == "Moto" and v["status"] == "Livre" and not v["interditada"]]
        return candidatas[0] if candidatas else None

    comuns = [v for v in vagas if v["tipo"] == "Comum" and v["status"] == "Livre" and not v["interditada"]]
    if comuns:
        return comuns[0]
    preferenciais = [v for v in vagas if v["tipo"] == "Preferencial" and v["status"] == "Livre" and not v["interditada"]]
    return preferenciais[0] if preferenciais else None
