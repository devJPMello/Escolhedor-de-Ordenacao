"""escolher(v) olha a lista e devolve o método mais adequado; ordenar(v) executa.

As constantes abaixo vieram de bench/calibrar.py (ver RELATORIO.md).
"""
from itertools import islice
from operator import gt

from .metodos import (LIMITE_FAIXA_CONTAGEM, base, contagem, hibrida,
                      insercao)

# Até este tamanho a inserção ganha de tudo (sem recursão, sem listas auxiliares).
LIMIAR_PEQUENA = 16
# Fração máxima de "descidas" (v[i] > v[i+1]) para considerar a lista quase ordenada.
FRACAO_QUASE = 0.02
# Contagem só se a faixa de valores for no máximo FATOR_FAIXA * n.
FATOR_FAIXA = 1
# Base só compensa a partir deste tamanho (abaixo dele a híbrida ganha).
LIMIAR_BASE = 400


def escolher(v, com_nome=False):
    """Devolve a função de ordenação escolhida (ou (nome, função) se com_nome).

    Custo: no pior caso 3 passadas feitas em C (descidas, tipos, min/max).
    Em Python isso sai mais barato que 1 passada escrita em Python — medimos.
    Cada regra decide o mais cedo possível, sem olhar o resto.
    """
    n = len(v)
    if n <= LIMIAR_PEQUENA:
        nome, f = "insercao", insercao
    else:
        try:
            descidas = sum(map(gt, v, islice(v, 1, None)))
        except TypeError:  # elementos não comparáveis entre si: deixa o erro para o método
            descidas = n
        if descidas <= FRACAO_QUASE * n:
            nome, f = "insercao", insercao
        elif set(map(type, v)) != {int}:
            nome, f = "hibrida", hibrida
        else:
            faixa = max(v) - min(v) + 1
            if faixa <= FATOR_FAIXA * n and faixa <= LIMITE_FAIXA_CONTAGEM:
                nome, f = "contagem", contagem
            elif n >= LIMIAR_BASE:
                nome, f = "base", base
            else:
                nome, f = "hibrida", hibrida
    return (nome, f) if com_nome else f


def escolher_uma_passada(v):
    """Versão alternativa: uma única passada escrita em Python.

    Mantida só para comparação no calibrar.py (é mais lenta que escolher()).
    Devolve o nome do método escolhido com as mesmas regras.
    """
    n = len(v)
    if n <= LIMIAR_PEQUENA:
        return "insercao"
    ant = v[0]
    mn = mx = ant
    descidas = 0
    inteiros = type(ant) is int
    for x in islice(v, 1, None):
        if x < ant:
            descidas += 1
        if x < mn:
            mn = x
        elif x > mx:
            mx = x
        if inteiros and type(x) is not int:
            inteiros = False
        ant = x
    if descidas <= FRACAO_QUASE * n:
        return "insercao"
    if not inteiros:
        return "hibrida"
    faixa = mx - mn + 1
    if faixa <= FATOR_FAIXA * n and faixa <= LIMITE_FAIXA_CONTAGEM:
        return "contagem"
    return "base" if n >= LIMIAR_BASE else "hibrida"


def ordenar(v):
    return escolher(v)(v)
