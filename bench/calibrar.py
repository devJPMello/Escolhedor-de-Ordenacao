"""Experimentos que deram origem às constantes do escolhedor.

Uso:  python -m bench.calibrar
Cada bloco imprime uma tabela; o ponto de virada vira a constante correspondente.
"""
import random
import statistics
import time

from bench import cenarios
from ordenacao import metodos
from ordenacao.escolhedor import escolher, escolher_uma_passada


def ms(f, *args, rep=5, loops=1):
    amostras = []
    for _ in range(rep):
        t0 = time.perf_counter()
        for _ in range(loops):
            f(*args)
        amostras.append((time.perf_counter() - t0) * 1000 / loops)
    return statistics.median(amostras)


def aleatoria(n, faixa=10**9, seed=1):
    rng = random.Random(seed)
    return [rng.randint(-faixa, faixa) for _ in range(n)]


def bloco(titulo):
    print(f"\n=== {titulo} ===")


def lista_pequena():
    bloco("LIMIAR_PEQUENA: inserção x híbrida x intercalação (µs por lista)")
    print(f"{'n':>5} {'insercao':>10} {'hibrida':>10} {'intercal.':>10} {'rapida':>10}")
    for n in (4, 8, 16, 24, 32, 48, 64, 96, 128):
        v = aleatoria(n)
        loops = max(10, 20000 // n)
        t = [1000 * ms(f, v, loops=loops) for f in
             (metodos.insercao, metodos.hibrida, metodos.intercalacao, metodos.rapida)]
        print(f"{n:5d} " + " ".join(f"{x:10.2f}" for x in t))


def corte_hibrida():
    bloco("CORTE_HIBRIDA: tamanho do subvetor que vai para a inserção (n=20000)")
    v = aleatoria(20000)
    original = metodos.CORTE_HIBRIDA
    for corte in (1, 4, 8, 12, 16, 24, 32, 48):
        metodos.CORTE_HIBRIDA = corte
        random.seed(0)
        print(f"corte={corte:3d}  {ms(metodos.hibrida, v):8.2f} ms")
    metodos.CORTE_HIBRIDA = original


def fator_faixa():
    bloco("FATOR_FAIXA: contagem x base x híbrida variando faixa/n (n=5000)")
    n = 5000
    print(f"{'faixa/n':>8} {'contagem':>10} {'base':>10} {'hibrida':>10}")
    for fator in (0.02, 0.5, 1, 2, 4, 8, 16, 64, 200):
        k = max(1, int(fator * n))
        rng = random.Random(3)
        v = [rng.randrange(k) for _ in range(n)]
        t = [ms(f, v) for f in (metodos.contagem, metodos.base, metodos.hibrida)]
        print(f"{fator:8.2f} " + " ".join(f"{x:10.2f}" for x in t))


def limiar_base():
    bloco("LIMIAR_BASE: base x híbrida com chaves grandes (ms)")
    print(f"{'n':>6} {'base':>10} {'hibrida':>10} {'intercal.':>10}")
    for n in (33, 64, 128, 256, 512, 1000, 5000, 20000):
        v = aleatoria(n)
        loops = max(1, 2000 // n)
        t = [ms(f, v, loops=loops) for f in (metodos.base, metodos.hibrida, metodos.intercalacao)]
        print(f"{n:6d} " + " ".join(f"{x:10.3f}" for x in t))


def fracao_quase():
    bloco("FRACAO_QUASE: inserção x híbrida conforme a fração de descidas (n=5000)")
    print(f"{'trocas':>7} {'descidas/n':>11} {'insercao':>10} {'hibrida':>10}")
    for frac in (0.001, 0.005, 0.01, 0.02, 0.05, 0.1):
        v = cenarios.quase_ordenado(5000, frac, random.Random(7))
        d = sum(a > b for a, b in zip(v, v[1:])) / len(v)
        t = [ms(f, v) for f in (metodos.insercao, metodos.hibrida)]
        print(f"{frac:7.3f} {d:11.4f} " + " ".join(f"{x:10.2f}" for x in t))
    print("Trocas LONGAS (posições quaisquer) com a mesma fração — inserção sofre:")
    for frac in (0.001, 0.005, 0.01):
        rng = random.Random(7)
        v = list(range(5000))
        for _ in range(int(frac * 5000)):
            i, j = rng.randrange(5000), rng.randrange(5000)
            v[i], v[j] = v[j], v[i]
        d = sum(a > b for a, b in zip(v, v[1:])) / len(v)
        t = [ms(f, v) for f in (metodos.insercao, metodos.hibrida)]
        print(f"{frac:7.3f} {d:11.4f} " + " ".join(f"{x:10.2f}" for x in t))


def custo_escolher():
    bloco("Custo do escolher: passadas em C (atual) x uma passada em Python (ms)")
    for n in (1000, 5000, 20000):
        v = aleatoria(n)
        print(f"n={n:6d}  C: {ms(escolher, v, loops=20):7.3f}   "
              f"Python 1 passada: {ms(escolher_uma_passada, v, loops=20):7.3f}   "
              f"(híbrida sozinha: {ms(metodos.hibrida, v):8.2f})")


if __name__ == "__main__":
    lista_pequena()
    corte_hibrida()
    fator_faixa()
    limiar_base()
    fracao_quase()
    custo_escolher()
