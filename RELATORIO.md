# Relatório — Escolhedor de Ordenação

**Dupla:** João Pedro e Lucas Vieira

Medições feitas em Python 3.13, Windows 11, com `python -m bench.medir --rep 7`
(mediana de 7 execuções; todas as saídas conferidas contra `sorted()`).
Os tempos absolutos dependem da máquina; o que importa são as proporções.

## 1. Cenários

| cenário | como é gerado |
|---|---|
| aleatório, chaves grandes | n = 5000 inteiros uniformes em [−10⁹, 10⁹] |
| faixa estreita | n = 5000 inteiros em [0, 99] |
| quase ordenado | 5000 chaves grandes ordenadas; 1% dos elementos trocados com um vizinho a até 8 posições |
| lista minúscula | 2000 listas de 10 inteiros grandes; o tempo é o de ordenar todas |

## 2. Tabela: quatro cenários × seis métodos (ms)

Negrito = melhor método fixo do cenário.

| cenário | inserção | intercalação | rápida | híbrida | contagem | base | **ordenar** | escolhido |
|---|---|---|---|---|---|---|---|---|
| aleatório, chaves grandes | 361.64 | 6.36 | 6.19 | 5.01 | estoura¹ | **1.64** | 1.84 | base |
| faixa estreita | 338.85 | 6.21 | 2.25 | 2.23 | **0.24** | 0.33 | 0.43 | contagem |
| quase ordenado | **0.34** | 4.27 | 6.04 | 5.01 | estoura¹ | 1.49 | 0.43 | inserção |
| lista minúscula | **3.11** | 9.97 | 8.94 | 3.14 | estoura¹ | 109.56 | 3.25 | inserção |
| **total dos quatro** | 703.94 | 26.81 | 23.43 | 15.39 | não roda | 113.01 | **5.95** | |

¹ A faixa (≈ 2·10⁹ valores) passaria do limite de 10⁶ contadores; a contagem se recusa a rodar.
Uma contagem "ingênua" tentaria alocar uma lista de 2 bilhões de posições (≈ 16 GB).

**Resultado:** o `ordenar` escolheu o melhor método nos quatro cenários. Somando os quatro,
leva 5,95 ms, contra 15,39 ms da melhor escolha fixa (híbrida), ou seja, **2,6× mais rápido**.
Nenhum método fixo chega perto em todos os cenários: a base, que vence o aleatório, é 35× pior
que a inserção nas listas minúsculas; a inserção, que vence as minúsculas e as quase ordenadas,
leva 220× o tempo da base no aleatório.

## 3. Quem venceu cada cenário, e por quê

- **Aleatório, chaves grandes → base.** Com chaves de 31 bits a base faz 4 passadas lineares
  (dígitos de 8 bits), ≈ 4n operações simples. Os métodos por comparação fazem ≈ n·log₂n ≈ 61 000
  comparações, cada uma cara em Python. A contagem não roda (faixa enorme). A inserção é O(n²).
- **Faixa estreita → contagem.** Com só 100 valores possíveis, a contagem faz uma passada para
  contar e monta a saída com `extend` (em C). A base também vai bem (uma passada só, porque
  todos os valores cabem em um dígito), mas cria 256 baldes. A rápida em 3 vias (2,25 ms)
  ganha da intercalação porque os repetidos caem no trecho do meio e não são mais tocados.
- **Quase ordenado → inserção.** A inserção custa O(n + inversões). Com deslocamentos curtos
  há poucas inversões, então é praticamente uma passada. Os outros fazem todo o trabalho
  de sempre, sem aproveitar a ordem que já existe.
- **Lista minúscula → inserção** (a híbrida empata: com n ≤ 16 ela simplesmente chama a
  inserção). Para n = 10 o que pesa é o custo fixo de cada chamada: recursão e listas
  auxiliares (intercalação), sorteio do pivô (rápida) e, principalmente, criar 256 baldes por
  passada (base). Por isso a base, que é a melhor no aleatório grande, é a pior aqui.

## 4. As regras do `escolher` e de onde vieram

Aplicadas em ordem, parando na primeira que decide (código em
[ordenacao/escolhedor.py](ordenacao/escolhedor.py)):

| # | condição | método | constante |
|---|---|---|---|
| 1 | `n ≤ 16` | inserção | `LIMIAR_PEQUENA = 16` |
| 2 | descidas (`v[i] > v[i+1]`) ≤ 2% de n | inserção | `FRACAO_QUASE = 0.02` |
| 3 | algum elemento não é `int` (float, str, bool...) | híbrida | — |
| 4 | faixa `max − min + 1 ≤ n` **e** ≤ 10⁶ | contagem | `FATOR_FAIXA = 1`, `LIMITE_FAIXA_CONTAGEM` |
| 5 | inteiros com `n ≥ 400` | base | `LIMIAR_BASE = 400` |
| 6 | o resto | híbrida | — |

Todas as constantes saíram de `python -m bench.calibrar`:

**Regra 1 (lista pequena).** Tempo por lista, em µs:

| n | 4 | 8 | 16 | 24 | 32 | 48 | 64 |
|---|---|---|---|---|---|---|---|
| inserção | 0.38 | 1.14 | 3.25 | 6.64 | 10.85 | 27.68 | 44.74 |
| híbrida | 0.46 | 1.44 | 3.21 | 6.13 | 9.37 | 17.05 | 23.91 |

A inserção ganha até n ≈ 16 e perde dali em diante. O mesmo experimento, variando o tamanho
em que a híbrida passa para a inserção (n = 20 000), deu o melhor tempo com corte 16
(23,7 ms, contra 30,6 ms sem corte), daí `CORTE_HIBRIDA = 16`.

**Regra 2 (quase ordenado).** Com deslocamentos curtos a inserção ganhou da híbrida em todas
as frações testadas (0,78 ms contra 6,35 ms mesmo com 15% de descidas). Com trocas entre
posições **quaisquer** ela perde a partir de ≈ 1% de descidas (16 ms contra 6 ms com 2%).
Como o escolhedor não consegue distinguir os dois casos de graça (ver seção 6), escolhemos 2%:
nos casos comuns o ganho é de ~12×, e no pior caso dentro desse limite a perda é de ~2,7×.

**Regra 4 (contagem).** n = 5000, variando a razão faixa/n (ms):

| faixa/n | 0.02 | 0.5 | 1 | 2 | 4 | 16 | 64 | 200 |
|---|---|---|---|---|---|---|---|---|
| contagem | 0.36 | 0.62 | 0.76 | 1.07 | 1.55 | 3.62 | 11.64 | 30.59 |
| base | 0.53 | 0.66 | 0.98 | 0.85 | 1.36 | 1.63 | 1.79 | 1.30 |

A contagem só ganha da base até faixa ≈ n; depois o vetor de contadores (que é percorrido
inteiro) domina. O limite absoluto de 10⁶ é o aviso da memória: mesmo com n enorme, a
contagem nunca é chamada com uma faixa que peça mais que ≈ 8 MB de contadores. O teste
`test_faixa_enorme_nunca_vai_para_contagem` verifica isso.

**Regra 5 (base).** Chaves grandes, ms:

| n | 64 | 128 | 256 | 512 | 1000 | 5000 | 20000 |
|---|---|---|---|---|---|---|---|
| base | 0.090 | 0.111 | 0.209 | 0.297 | 0.557 | 2.18 | 8.11 |
| híbrida | 0.030 | 0.073 | 0.165 | 0.503 | 0.988 | 5.67 | 33.04 |

A virada fica entre 256 e 512; usamos 400.

**Regra 3** não vem de medição: contagem e base só funcionam com inteiros, então qualquer
outro tipo vai para a híbrida, que é a mais rápida entre os métodos por comparação em todos
os cenários. `bool` é tratado como não-inteiro de propósito.

## 5. Quanto custa o `escolher` — compensa?

O `escolher` faz no máximo três coisas, cada uma uma passada feita **em C** pelo interpretador:
`sum(map(gt, v, v[1:]))` para as descidas, `set(map(type, v))` para os tipos, e `min`/`max`.
Para n = 5000 isso custa ≈ 0,21 ms (descidas 0,084 + tipos 0,053 + min/max 0,061).

Sobre o aviso de que percorrer a lista duas vezes pode anular o ganho: testamos também uma
versão com **uma única passada escrita em Python** (`escolher_uma_passada`). Ela foi mais
lenta (0,34 ms contra 0,25 ms para n = 5000). Em Python, o que pesa é quantas operações
passam pelo interpretador, não quantas vezes a lista é percorrida.
Além disso, cada regra para o mais cedo possível: listas pequenas decidem só com `len`, e as
quase ordenadas decidem depois da primeira passada.

| cenário | custo do escolher | % do tempo do `ordenar` |
|---|---|---|
| aleatório, chaves grandes | 0.209 ms | 11% |
| faixa estreita | 0.207 ms | 48% |
| quase ordenado | 0.086 ms | 20% |
| lista minúscula (2000 listas) | 0.114 ms | 3.5% |

**Compensa:** errar de método custa muito mais que o escolher. No pior caso medido (faixa
estreita) ele quase dobra o tempo da contagem, e o `ordenar` (0,43 ms) fica um pouco atrás da
base fixa (0,33 ms), mas ainda 5× à frente da híbrida, que é a melhor escolha fixa no total.
Nos quatro cenários juntos o `ordenar` é 2,6× mais rápido que qualquer método fixo.
Melhoria possível: repassar o `min`/`max` já calculado para a contagem, que hoje calcula de novo.

## 6. Um cenário em que ele erra

**Duas metades ordenadas trocadas:** `[2500, 2501, ..., 4999, 0, 1, ..., 2499]`.

| | inserção | intercalação | rápida | híbrida | contagem | base | **ordenar** |
|---|---|---|---|---|---|---|---|
| metades trocadas (ms) | 359.92 | 4.28 | 6.58 | 5.48 | 0.74 | **0.69** | 359.52 |

A lista tem **uma única descida** (entre 4999 e 0), então a regra 2 a considera quase ordenada
e manda para a inserção. Mas cada um dos 2500 elementos da segunda metade precisa passar por
todos os 2500 da primeira: são n²/4 ≈ 6,25 milhões de inversões, e a inserção leva 360 ms,
**520× mais** que a base.

O motivo: contar descidas mede quantos "pedaços" ordenados a lista tem, não **quão longe** os
elementos estão do lugar certo. Contar as inversões resolveria, mas custa O(n log n), o mesmo
que ordenar. O mesmo problema, em menor grau, aparece com poucas trocas entre posições
distantes (seção 4, regra 2). Uma correção barata seria mudar a regra 2 para "poucas descidas
**e** cada descida pequena" (por exemplo, `v[i] − v[i+1]` menor que uma fração da faixa), o que
pegaria este caso ao custo de mais uma passada.

## 7. Testes

`python -m unittest -v` roda 13 testes (com subtestes para cada combinação de método e caso):
lista vazia, um elemento, todos iguais, já ordenada, invertida, valores negativos, só negativos,
listas aleatórias de vários tamanhos e faixas, floats nos métodos por comparação, recusa da
contagem com faixa enorme, e as decisões do `escolher` (inclusive que ele nunca escolhe
contagem para faixas grandes e nunca escolhe contagem/base para não-inteiros).
