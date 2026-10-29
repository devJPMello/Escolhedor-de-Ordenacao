"""Os seis métodos de ordenação do semestre.

Todos recebem uma lista e devolvem uma NOVA lista ordenada (a entrada não é alterada).
"""
import random

# Acima desta faixa (max - min + 1) a contagem se recusa a rodar: o vetor de
# contadores ficaria grande demais. O escolhedor usa o mesmo limite antes de chamá-la.
LIMITE_FAIXA_CONTAGEM = 1_000_000

# Tamanho de subvetor a partir do qual a híbrida troca a rápida pela inserção.
CORTE_HIBRIDA = 16


def _insercao_trecho(a, ini, fim):
    """Inserção no trecho a[ini..fim], inclusive, no lugar."""
    for i in range(ini + 1, fim + 1):
        x = a[i]
        j = i - 1
        while j >= ini and a[j] > x:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = x


def insercao(v):
    a = list(v)
    _insercao_trecho(a, 0, len(a) - 1)
    return a


def intercalacao(v):
    a = list(v)
    if len(a) <= 1:
        return a
    meio = len(a) // 2
    esq = intercalacao(a[:meio])
    dir_ = intercalacao(a[meio:])
    saida = []
    i = j = 0
    while i < len(esq) and j < len(dir_):
        if esq[i] <= dir_[j]:
            saida.append(esq[i])
            i += 1
        else:
            saida.append(dir_[j])
            j += 1
    saida.extend(esq[i:])
    saida.extend(dir_[j:])
    return saida


def _particao_3vias(a, ini, fim):
    """Partição de Dijkstra com pivô aleatório.

    Deixa a[ini..lt-1] < pivô, a[lt..gt] == pivô, a[gt+1..fim] > pivô e devolve (lt, gt).
    Com muitos repetidos (ou todos iguais) o trecho do meio absorve tudo e não há O(n²).
    """
    p = random.randint(ini, fim)
    pivo = a[p]
    lt, i, gt = ini, ini, fim
    while i <= gt:
        x = a[i]
        if x < pivo:
            a[lt], a[i] = x, a[lt]
            lt += 1
            i += 1
        elif x > pivo:
            a[gt], a[i] = x, a[gt]
            gt -= 1
        else:
            i += 1
    return lt, gt


def _rapida_trecho(a, ini, fim, corte):
    # Recursão só no lado menor e laço no maior: pilha fica O(log n).
    while fim - ini + 1 > corte:
        lt, gt = _particao_3vias(a, ini, fim)
        if lt - ini < fim - gt:
            _rapida_trecho(a, ini, lt - 1, corte)
            ini = gt + 1
        else:
            _rapida_trecho(a, gt + 1, fim, corte)
            fim = lt - 1
    if corte > 1 and fim > ini:
        _insercao_trecho(a, ini, fim)


def rapida(v):
    a = list(v)
    _rapida_trecho(a, 0, len(a) - 1, 1)
    return a


def hibrida(v):
    a = list(v)
    _rapida_trecho(a, 0, len(a) - 1, CORTE_HIBRIDA)
    return a


def contagem(v):
    """Só para inteiros. Aceita negativos deslocando pelo mínimo."""
    if not v:
        return []
    m = min(v)
    k = max(v) - m + 1
    if k > LIMITE_FAIXA_CONTAGEM:
        raise MemoryError(f"faixa {k} grande demais para a contagem")
    cont = [0] * k
    for x in v:
        cont[x - m] += 1
    saida = []
    for i, c in enumerate(cont):
        if c:
            saida.extend([i + m] * c)
    return saida


def base(v):
    """Radix LSD em base 256, só para inteiros. Negativos: desloca tudo por -min."""
    if not v:
        return []
    m = min(v)
    a = [x - m for x in v] if m else list(v)
    maior = max(a)
    desloc = 0
    while (maior >> desloc) > 0:
        baldes = [[] for _ in range(256)]
        for x in a:
            baldes[(x >> desloc) & 255].append(x)
        a = [x for b in baldes for x in b]
        desloc += 8
    return [x + m for x in a] if m else a


METODOS = {
    "insercao": insercao,
    "intercalacao": intercalacao,
    "rapida": rapida,
    "hibrida": hibrida,
    "contagem": contagem,
    "base": base,
}
