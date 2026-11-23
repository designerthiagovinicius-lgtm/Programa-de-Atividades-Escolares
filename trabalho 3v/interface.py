"""Módulo de interface: telas e menus do terminal."""

import getpass

import armazenamento
import atividades as regras
import usuarios as contas

MAX_TENTATIVAS = 3

MENU_LOGIN = """
==============================
   LISTA DE ATIVIDADES
==============================
1 - Entrar
2 - Criar conta
0 - Fechar programa
"""

MENU_PRINCIPAL = """
===== MENU - {usuario} =====
1 - Cadastrar atividade
2 - Atualizar atividade
3 - Excluir atividade
4 - Marcar como concluída
5 - Listar atividades
0 - Sair da conta (logout)
"""

MENU_LISTAGEM = """
===== LISTAR ATIVIDADES =====
1 - Todas
2 - Pendentes
3 - Concluídas
4 - Pendentes por prioridade (maior primeiro)
5 - Filtrar por uma prioridade
6 - Buscar por nome
7 - Resumo / estatísticas
0 - Voltar
"""


# ---------- Entradas ----------
def ler_id():
    try:
        return int(input("ID da atividade: ").strip())
    except ValueError:
        print("ID inválido.")
        return None


def ler_prioridade(atual=None):
    print("Prioridade: 1 - Baixa | 2 - Média | 3 - Alta")
    dica = f" (Enter mantém {atual})" if atual else ""
    op = input(f"Escolha{dica}: ").strip()
    if not op:
        return atual or "Baixa"
    if op in ("1", "2", "3"):
        return regras.PRIORIDADES[int(op) - 1]
    print("Opção inválida, usando o valor padrão.")
    return atual or "Baixa"


# ---------- Saídas ----------
def mostrar(lista, titulo):
    print(f"\n=== {titulo} ===")
    if not lista:
        print("Nenhuma atividade.")
        return
    for a in lista:
        marca = "[x]" if a["concluida"] else "[ ]"
        extra = f" | concluída em {a['concluida_em']}" if a["concluida"] else ""
        print(f"{marca} #{a['id']} {a['nome']} | Prioridade: {a['prioridade']} "
              f"| criada em {a['criada_em']}{extra}")
    print(f"({len(lista)} atividade(s))")


def mostrar_resumo(lista):
    r = regras.resumo(lista)
    print("\n=== Resumo ===")
    print(f"Total: {r['total']} | Concluídas: {r['concluidas']} | Pendentes: {r['pendentes']}")
    print(f"Progresso: {r['percentual']}% concluído")
    print("Pendentes por prioridade: " + ", ".join(
        f"{p}: {q}" for p, q in r["pendentes_por_prioridade"].items()))


# ---------- Login e cadastro de conta ----------
def tela_criar_conta():
    print("\n--- Criar conta ---")
    login = input("Login (3-20 letras, números ou _): ")
    senha = getpass.getpass("Senha: ")
    confirmacao = getpass.getpass("Confirme a senha: ")
    if senha != confirmacao:
        print("As senhas não conferem.")
        return
    lista = armazenamento.carregar_usuarios()
    try:
        novo = contas.cadastrar(lista, login, senha)
    except ValueError as erro:
        print(erro)
        return
    armazenamento.salvar_usuarios(lista)
    print(f"Conta '{novo}' criada! Agora é só entrar.")


def tela_login():
    """Retorna o login do usuário autenticado ou None."""
    print("\n--- Entrar ---")
    registros = armazenamento.carregar_usuarios()
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        login = input("Login: ")
        senha = getpass.getpass("Senha: ")
        try:
            return contas.autenticar(registros, login, senha)
        except ValueError as erro:
            restantes = MAX_TENTATIVAS - tentativa
            print(f"{erro} ({restantes} tentativa(s) restante(s))" if restantes else erro)
    print("Número máximo de tentativas atingido.")
    return None


# ---------- Ações do menu principal ----------
def acao_cadastrar(lista):
    nome = input("Nome da atividade: ")
    prioridade = ler_prioridade()
    regras.cadastrar(lista, nome, prioridade)
    print("Atividade cadastrada!")


def acao_atualizar(lista):
    id_ = ler_id()
    if id_ is None:
        return
    atividade = regras.buscar(lista, id_)
    if atividade is None:
        print("Atividade não encontrada.")
        return
    nome = input(f"Novo nome (Enter mantém '{atividade['nome']}'): ")
    prioridade = ler_prioridade(atividade["prioridade"])
    regras.atualizar(lista, id_, nome, prioridade)
    print("Atividade atualizada!")


def acao_excluir(lista):
    id_ = ler_id()
    if id_ is not None:
        regras.excluir(lista, id_)
        print("Atividade excluída!")


def acao_concluir(lista):
    id_ = ler_id()
    if id_ is not None:
        regras.concluir(lista, id_)
        print("Atividade marcada como concluída!")


ACOES_QUE_SALVAM = {
    "1": acao_cadastrar,
    "2": acao_atualizar,
    "3": acao_excluir,
    "4": acao_concluir,
}


# ---------- Submenu de listagem ----------
def menu_listagem(lista):
    while True:
        print(MENU_LISTAGEM)
        op = input("Escolha uma opção: ").strip()
        if op == "0":
            return
        elif op == "1":
            mostrar(regras.todas(lista), "Todas as atividades")
        elif op == "2":
            mostrar(regras.pendentes(lista), "Atividades pendentes")
        elif op == "3":
            mostrar(regras.concluidas(lista), "Atividades concluídas")
        elif op == "4":
            mostrar(regras.pendentes_por_prioridade(lista),
                    "Pendentes por prioridade (maior primeiro)")
        elif op == "5":
            prioridade = ler_prioridade()
            mostrar(regras.filtrar_por_prioridade(lista, prioridade),
                    f"Atividades de prioridade {prioridade}")
        elif op == "6":
            termo = input("Buscar por: ")
            mostrar(regras.buscar_por_nome(lista, termo), f"Resultado da busca por '{termo.strip()}'")
        elif op == "7":
            mostrar_resumo(lista)
        else:
            print("Opção inválida.")


# ---------- Sessão do usuário logado ----------
def sessao(usuario):
    lista = armazenamento.carregar_atividades(usuario)
    print(f"\nBem-vindo(a), {usuario}!")
    while True:
        print(MENU_PRINCIPAL.format(usuario=usuario))
        op = input("Escolha uma opção: ").strip()
        if op == "0":
            print("Sessão encerrada.")
            return
        try:
            if op in ACOES_QUE_SALVAM:
                ACOES_QUE_SALVAM[op](lista)
                armazenamento.salvar_atividades(usuario, lista)
            elif op == "5":
                menu_listagem(lista)
            else:
                print("Opção inválida.")
        except ValueError as erro:
            print(erro)


# ---------- Programa ----------
def executar():
    while True:
        print(MENU_LOGIN)
        op = input("Escolha uma opção: ").strip()
        if op == "0":
            print("Até logo!")
            break
        elif op == "1":
            usuario = tela_login()
            if usuario:
                sessao(usuario)
        elif op == "2":
            tela_criar_conta()
        else:
            print("Opção inválida.")
