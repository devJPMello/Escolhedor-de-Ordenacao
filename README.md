# Escolhedor de Ordenação

**Dupla:** João Pedro e Lucas Vieira

Um `ordenar(v)` que olha a lista, escolhe sozinho entre seis métodos (inserção,
intercalação, rápida com pivô aleatório, híbrida, contagem e base) e executa o escolhido.
Resultados e discussão em [RELATORIO.md](RELATORIO.md).

## Requisitos

Python 3.10 ou mais novo. Só a biblioteca padrão, nada para instalar.

## Uso

```python
from ordenacao import ordenar, escolher

ordenar([5, -2, 9, 0])                 # [-2, 0, 5, 9]
escolher([5, -2, 9, 0], com_nome=True) # ('insercao', <function insercao>)
```

## Organização

| caminho | conteúdo |
|---|---|
| `ordenacao/metodos.py` | os seis métodos (todos devolvem uma lista nova) |
| `ordenacao/escolhedor.py` | `escolher(v)`, `ordenar(v)` e as constantes das regras |
| `bench/cenarios.py` | geradores dos cenários, com semente fixa |
| `bench/medir.py` | mede os 6 métodos + `ordenar` nos 4 cenários e no cenário de erro |
| `bench/calibrar.py` | experimentos que deram origem às constantes do escolhedor |
| `resultados/` | `tabela.md` e `resultados.csv` gerados pelo `medir.py` |
| `tests/` | testes (`unittest`) |

## Rodar os testes

Na raiz do repositório:

```
python -m unittest -v
```

Cobrem lista vazia, um elemento, todos iguais, já ordenada, invertida, negativos e listas
aleatórias para todos os métodos e o `ordenar`, mais as decisões do `escolher`.

## Refazer as medições

Na raiz do repositório:

```
python -m bench.calibrar          # pontos de virada que viraram as constantes (~1 min)
python -m bench.medir             # tabela principal, mediana de 5 execuções (~15 s)
python -m bench.medir --rep 9     # mais repetições, se quiser menos ruído
```

O `medir.py` imprime a tabela e grava `resultados/tabela.md` e `resultados/resultados.csv`.
As listas são sempre as mesmas (semente fixa), mas os tempos absolutos mudam de máquina para
máquina; as proporções entre os métodos é que devem se repetir. Para medir com menos ruído,
feche outros programas e deixe o notebook na tomada.

Se o terminal do Windows mostrar acentos quebrados, rode antes `set PYTHONIOENCODING=utf-8`
(cmd) ou `$env:PYTHONIOENCODING="utf-8"` (PowerShell). Os arquivos gravados não são afetados.
