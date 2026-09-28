"""
Funções auxiliares de interface (terminal) e validação de entradas
do usuário. Nenhuma função aqui depende de dados de negócio — são
utilitários puros reutilizados por todos os outros módulos.
"""

import os
from datetime import datetime


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\nPressione ENTER para continuar...")


def ler_texto(mensagem, obrigatorio=True):
    """Lê uma string do usuário, validando que não esteja vazia
    (a menos que 'obrigatorio' seja False)."""
    while True:
        valor = input(mensagem).strip()
        if valor or not obrigatorio:
            return valor
        print("⚠ Este campo não pode ficar vazio. Tente novamente.")


def ler_inteiro(mensagem, minimo=None, maximo=None):
    """Lê um número inteiro validado, dentro de uma faixa opcional."""
    while True:
        valor = input(mensagem).strip()
        try:
            numero = int(valor)
        except ValueError:
            print("⚠ Digite um número inteiro válido.")
            continue
        if minimo is not None and numero < minimo:
            print(f"⚠ O valor deve ser maior ou igual a {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            print(f"⚠ O valor deve ser menor ou igual a {maximo}.")
            continue
        return numero


def ler_opcao(mensagem, opcoes_validas):
    """Valida a escolha de um menu (lista de strings numéricas)."""
    while True:
        escolha = input(mensagem).strip()
        if escolha in opcoes_validas:
            return escolha
        print(f"⚠ Opção inválida. Escolha uma das opções: {', '.join(opcoes_validas)}")


def ler_opcao_lista(mensagem, lista):
    """Exibe uma lista numerada de opções e retorna o item escolhido."""
    for indice, item in enumerate(lista, start=1):
        print(f"  {indice}. {item}")
    escolha = ler_inteiro(mensagem, 1, len(lista))
    return lista[escolha - 1]


def ler_sim_nao(mensagem):
    while True:
        resposta = input(mensagem + " (S/N): ").strip().upper()
        if resposta in ("S", "N"):
            return resposta == "S"
        print("⚠ Responda apenas com S ou N.")


def ler_placa(mensagem):
    """Valida um formato simples de placa (5 a 8 caracteres alfanuméricos)."""
    while True:
        placa = input(mensagem).strip().upper().replace(" ", "").replace("-", "")
        if 5 <= len(placa) <= 8 and placa.isalnum():
            return placa
        print("⚠ Placa inválida. Utilize um formato como ABC1234 ou ABC1D23.")


def ler_data(mensagem):
    """Lê uma data no formato DD/MM/AAAA, validando o formato."""
    while True:
        texto = input(mensagem).strip()
        try:
            return datetime.strptime(texto, "%d/%m/%Y")
        except ValueError:
            print("⚠ Data inválida. Utilize o formato DD/MM/AAAA.")


def proximo_id(lista):
    """Gera o próximo ID sequencial de uma lista de dicionários com chave 'id'."""
    return max((item["id"] for item in lista), default=0) + 1
