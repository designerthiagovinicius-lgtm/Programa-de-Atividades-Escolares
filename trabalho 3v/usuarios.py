"""Módulo de usuários: cadastro e autenticação (login e senha).

A senha NUNCA é guardada em texto puro. Guardamos apenas um 'hash' (resultado
de uma conta matemática de via única) junto com um 'salt' aleatório, para que
duas pessoas com a mesma senha não tenham o mesmo hash.
"""

import hashlib
import hmac
import re
import secrets

ITERACOES = 200_000
PADRAO_LOGIN = re.compile(r"^[a-z0-9_]{3,20}$")
TAMANHO_MIN_SENHA = 4


def _gerar_hash(senha, salt):
    return hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, ITERACOES)


def normalizar_login(login):
    return login.strip().lower()


def cadastrar(usuarios, login, senha):
    """Cria uma nova conta. Levanta ValueError se algo estiver inválido."""
    login = normalizar_login(login)
    if not PADRAO_LOGIN.match(login):
        raise ValueError("Login inválido: use de 3 a 20 letras, números ou _ (sem espaços).")
    if login in usuarios:
        raise ValueError("Esse login já está em uso.")
    if len(senha) < TAMANHO_MIN_SENHA:
        raise ValueError(f"A senha deve ter pelo menos {TAMANHO_MIN_SENHA} caracteres.")
    salt = secrets.token_bytes(16)
    usuarios[login] = {
        "salt": salt.hex(),
        "hash": _gerar_hash(senha, salt).hex(),
    }
    return login


def autenticar(usuarios, login, senha):
    """Retorna o login se estiver correto; senão levanta ValueError."""
    login = normalizar_login(login)
    dados = usuarios.get(login)
    # A mensagem é a mesma para login inexistente e senha errada (não revela qual deu erro).
    erro = ValueError("Login ou senha incorretos.")
    if dados is None:
        _gerar_hash(senha, b"0" * 16)  # gasta o mesmo tempo, para não vazar se o login existe
        raise erro
    esperado = bytes.fromhex(dados["hash"])
    calculado = _gerar_hash(senha, bytes.fromhex(dados["salt"]))
    if not hmac.compare_digest(esperado, calculado):
        raise erro
    return login
