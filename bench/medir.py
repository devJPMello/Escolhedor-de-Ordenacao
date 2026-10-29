"""Mede os seis métodos fixos e o ordenar() nos quatro cenários (+ o cenário de erro).

Uso:  python -m bench.medir            (5 repetições, mediana)
      python -m bench.medir --rep 9
Grava resultados/tabela.md e resultados/resultados.csv.
"""
import argparse
import csv
import random
import statistics
import time
from pathlib import Path

from bench.cenarios import CENARIO_ERRO, CENARIOS
from ordenacao import METODOS, escolher, ordenar

SAIDA = Path(__file__).resolve().parent.parent / "resultados"
COLUNAS = list(METODOS) + ["ordenar"]


def _tempo(f, entrada, lote, rep):
    """Mediana em ms de `rep` execuções. Devolve None se o método recusar a entrada."""
    amostras = []
    for _ in range(rep):
        random.seed(0)  # pivô aleatório reprodutível
        t0 = time.perf_counter()
        try:
            if lote:
                saidas = [f(v) for v in entrada]
            else:
                saidas = f(entrada)
        except MemoryError:
            return None
        amostras.append((time.perf_counter() - t0) * 1000)
    # confere que ordenou de verdade
    esperado = [sorted(v) for v in entrada] if lote else sorted(entrada)
    assert saidas == esperado, f"{f.__name__} ordenou errado"
    return statistics.median(amostras)


def _custo_escolher(entrada, lote, rep):
    amostras = []
    for _ in range(rep):
        t0 = time.perf_counter()
        if lote:
            for v in entrada:
                escolher(v)
        else:
            escolher(entrada)
        amostras.append((time.perf_counter() - t0) * 1000)
    return statistics.median(amostras)


def medir(cenarios, rep):
    linhas = []
    for nome, (gerar, lote) in cenarios.items():
        entrada = gerar()
        amostra = entrada[0] if lote else entrada
        escolhido = escolher(amostra, com_nome=True)[0]
        tempos = {}
        for col in COLUNAS:
            f = ordenar if col == "ordenar" else METODOS[col]
            tempos[col] = _tempo(f, entrada, lote, rep)
            print(f"  {nome:26s} {col:13s} "
                  f"{'estourou' if tempos[col] is None else f'{tempos[col]:9.2f} ms'}")
        fixos = {k: t for k, t in tempos.items() if k != "ordenar" and t is not None}
        linhas.append({
            "cenario": nome,
            **tempos,
            "escolhido": escolhido,
            "melhor_fixo": min(fixos, key=fixos.get),
            "custo_escolher": _custo_escolher(entrada, lote, rep),
        })
    return linhas


def _fmt(t):
    return "estoura*" if t is None else f"{t:.2f}"


def tabela_md(linhas, total=False):
    cab = "| cenário | " + " | ".join(COLUNAS) + " | escolhido | melhor fixo | custo do escolher |"
    sep = "|" + "---|" * (len(COLUNAS) + 4)
    corpo = []
    for l in linhas:
        melhor = l["melhor_fixo"]
        celulas = [f"**{_fmt(l[c])}**" if c == melhor else _fmt(l[c]) for c in COLUNAS]
        pct = 100 * l["custo_escolher"] / l["ordenar"]
        corpo.append(f"| {l['cenario']} | " + " | ".join(celulas) +
                     f" | {l['escolhido']} | {melhor} | {l['custo_escolher']:.3f} ms ({pct:.1f}%) |")
    if total:
        # soma dos cenários: quem estoura em algum cenário não tem total
        somas = {c: (None if any(l[c] is None for l in linhas) else sum(l[c] for l in linhas))
                 for c in COLUNAS}
        corpo.append("| **total** | " + " | ".join(
            "não roda" if somas[c] is None else f"{somas[c]:.2f}" for c in COLUNAS) + " | | | |")
    return "\n".join([cab, sep, *corpo])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rep", type=int, default=5)
    args = ap.parse_args()

    print("Medindo cenários principais...")
    linhas = medir(CENARIOS, args.rep)
    print("Medindo cenário de erro...")
    linhas_erro = medir(CENARIO_ERRO, args.rep)

    SAIDA.mkdir(exist_ok=True)
    md = ("Tempos em ms (mediana de %d execuções). Negrito = melhor método fixo.\n"
          "*contagem recusa faixas acima de 10^6 valores (estouraria a memória).\n\n"
          "## Cenários principais\n\n%s\n\n## Cenário de erro\n\n%s\n"
          % (args.rep, tabela_md(linhas, total=True), tabela_md(linhas_erro)))
    (SAIDA / "tabela.md").write_text(md, encoding="utf-8")
    with open(SAIDA / "resultados.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas + linhas_erro)
    print()
    print(md)


if __name__ == "__main__":
    main()
