"""Geradores dos cenários de medição. Semente fixa para dar sempre as mesmas listas."""
import random

SEMENTE = 2026
N = 5000


def aleatorio_chaves_grandes(n=N, rng=None):
    rng = rng or random.Random(SEMENTE)
    return [rng.randint(-10**9, 10**9) for _ in range(n)]


def faixa_estreita(n=N, rng=None):
    rng = rng or random.Random(SEMENTE)
    return [rng.randint(0, 99) for _ in range(n)]


def quase_ordenado(n=N, frac=0.01, rng=None):
    """Lista ordenada com frac*n elementos deslocados para perto (até 8 posições).

    É o "quase ordenado" típico: dados que chegam em ordem com pequenos atrasos.
    """
    rng = rng or random.Random(SEMENTE)
    # chaves grandes, para não confundir com o cenário de faixa estreita
    v = sorted(rng.randint(-10**9, 10**9) for _ in range(n))
    for _ in range(int(frac * n)):
        i = rng.randrange(n)
        j = min(n - 1, i + rng.randint(1, 8))
        v[i], v[j] = v[j], v[i]
    return v


def minusculas(qtd=2000, n=10, rng=None):
    """Várias listas pequenas (a medição soma o tempo de ordenar todas)."""
    rng = rng or random.Random(SEMENTE)
    return [[rng.randint(-10**9, 10**9) for _ in range(n)] for _ in range(qtd)]


def metades_trocadas(n=N):
    """Cenário em que o escolhedor erra: duas metades ordenadas, a de cima primeiro.

    Só 1 descida (parece quase ordenado), mas n²/4 inversões: péssimo para a inserção.
    """
    h = n // 2
    return list(range(h, n)) + list(range(h))


# nome -> (função que gera, é_lote). Um lote é uma lista de listas.
CENARIOS = {
    "aleatorio_chaves_grandes": (aleatorio_chaves_grandes, False),
    "faixa_estreita": (faixa_estreita, False),
    "quase_ordenado": (quase_ordenado, False),
    "lista_minuscula": (minusculas, True),
}

CENARIO_ERRO = {"metades_trocadas": (metades_trocadas, False)}
