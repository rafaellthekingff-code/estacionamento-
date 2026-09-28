"""
Camada de persistência: responsável por ler e gravar as listas de
dados (vagas, clientes, veículos, registros) em arquivos .txt,
usando JSON como formato interno. Isolar essa lógica aqui permite
trocar o mecanismo de armazenamento (ex: banco de dados) no futuro
sem impactar as regras de negócio.
"""

import os
import json

from . import config


def garantir_diretorio():
    """Garante que a pasta de dados exista antes de ler/gravar arquivos."""
    if not os.path.exists(config.DIRETORIO_DADOS):
        os.makedirs(config.DIRETORIO_DADOS)


def carregar_dados(caminho):
    """Carrega uma lista de dicionários a partir de um arquivo .txt.
    Trata exceções de leitura/formatação, retornando lista vazia em
    caso de falha, sem interromper o funcionamento do sistema."""
    garantir_diretorio()
    if not os.path.exists(caminho):
        return []
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read().strip()
            return json.loads(conteudo) if conteudo else []
    except (json.JSONDecodeError, OSError) as erro:
        print(f"[Aviso] Não foi possível ler {caminho}: {erro}. Iniciando lista vazia.")
        return []


def salvar_dados(caminho, dados):
    """Grava uma lista de dicionários em um arquivo .txt (formato JSON)."""
    garantir_diretorio()
    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    except OSError as erro:
        print(f"[Erro] Não foi possível salvar {caminho}: {erro}")
