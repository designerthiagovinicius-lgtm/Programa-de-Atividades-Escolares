"""Módulo de regras: operações e consultas sobre a lista de atividades.

Não tem input() nem print(): só lógica. Assim dá para reaproveitar em outra
interface (ex.: site ou app) e testar mais fácil.
"""

from datetime import date

PRIORIDADES = ("Baixa", "Média", "Alta")
PESO = {"Baixa": 1, "Média": 2, "Alta": 3}


# ---------- Auxiliares ----------
def _proximo_id(atividades):
    return max((a["id"] for a in atividades), default=0) + 1


def buscar(atividades, id_):
    for a in atividades:
        if a["id"] == id_:
            return a
    return None


def _buscar_ou_erro(atividades, id_):
    atividade = buscar(atividades, id_)
    if atividade is None:
        raise ValueError("Atividade não encontrada.")
    return atividade


# ---------- Operações (alteram a lista) ----------
def cadastrar(atividades, nome, prioridade="Baixa"):
    nome = nome.strip()
    if not nome:
        raise ValueError("O nome não pode ser vazio.")
    if prioridade not in PRIORIDADES:
        raise ValueError("Prioridade inválida.")
    atividade = {
        "id": _proximo_id(atividades),
        "nome": nome,
        "prioridade": prioridade,
        "concluida": False,
        "criada_em": date.today().isoformat(),
        "concluida_em": None,
    }
    atividades.append(atividade)
    return atividade


def atualizar(atividades, id_, nome=None, prioridade=None):
    atividade = _buscar_ou_erro(atividades, id_)
    if nome is not None and nome.strip():
        atividade["nome"] = nome.strip()
    if prioridade is not None:
        if prioridade not in PRIORIDADES:
            raise ValueError("Prioridade inválida.")
        atividade["prioridade"] = prioridade
    return atividade


def excluir(atividades, id_):
    atividade = _buscar_ou_erro(atividades, id_)
    atividades.remove(atividade)
    return atividade


def concluir(atividades, id_):
    atividade = _buscar_ou_erro(atividades, id_)
    if atividade["concluida"]:
        raise ValueError("Essa atividade já está concluída.")
    atividade["concluida"] = True
    atividade["concluida_em"] = date.today().isoformat()
    return atividade


# ---------- Consultas (só leitura) ----------
def todas(atividades):
    return sorted(atividades, key=lambda a: a["id"])


def pendentes(atividades):
    return [a for a in todas(atividades) if not a["concluida"]]


def concluidas(atividades):
    return [a for a in todas(atividades) if a["concluida"]]


def pendentes_por_prioridade(atividades):
    """Pendentes da maior para a menor prioridade (empate: a mais antiga primeiro)."""
    return sorted(pendentes(atividades), key=lambda a: (-PESO[a["prioridade"]], a["id"]))


def filtrar_por_prioridade(atividades, prioridade):
    """Todas as atividades (pendentes e concluídas) de uma prioridade específica."""
    return [a for a in todas(atividades) if a["prioridade"] == prioridade]


def buscar_por_nome(atividades, termo):
    termo = termo.strip().lower()
    return [a for a in todas(atividades) if termo in a["nome"].lower()]


def resumo(atividades):
    """Estatísticas gerais da lista."""
    total = len(atividades)
    feitas = len(concluidas(atividades))
    return {
        "total": total,
        "concluidas": feitas,
        "pendentes": total - feitas,
        "percentual": round(feitas / total * 100) if total else 0,
        "pendentes_por_prioridade": {
            p: sum(1 for a in pendentes(atividades) if a["prioridade"] == p)
            for p in reversed(PRIORIDADES)
        },
    }
