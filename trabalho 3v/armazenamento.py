"""Módulo de armazenamento: lê e grava os dados em arquivos JSON.

Estrutura de arquivos criada na pasta 'dados':
    dados/usuarios.json              -> contas (login + senha criptografada)
    dados/atividades_<usuario>.json  -> lista de atividades de cada usuário
"""

import json
import os

PASTA = "dados"


def _carregar(caminho, padrao):
    if not os.path.exists(caminho):
        return padrao
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return padrao


def _salvar(caminho, dados):
    os.makedirs(PASTA, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# ---------- Usuários ----------
def _arquivo_usuarios():
    return os.path.join(PASTA, "usuarios.json")


def carregar_usuarios():
    return _carregar(_arquivo_usuarios(), {})


def salvar_usuarios(usuarios):
    _salvar(_arquivo_usuarios(), usuarios)


# ---------- Atividades (uma lista por usuário) ----------
def _arquivo_atividades(usuario):
    return os.path.join(PASTA, f"atividades_{usuario}.json")


def carregar_atividades(usuario):
    return _carregar(_arquivo_atividades(usuario), [])


def salvar_atividades(usuario, atividades):
    _salvar(_arquivo_atividades(usuario), atividades)
