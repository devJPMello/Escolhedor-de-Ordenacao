Tempos em ms (mediana de 7 execuções). Negrito = melhor método fixo.
*contagem recusa faixas acima de 10^6 valores (estouraria a memória).

## Cenários principais

| cenário | insercao | intercalacao | rapida | hibrida | contagem | base | ordenar | escolhido | melhor fixo | custo do escolher |
|---|---|---|---|---|---|---|---|---|---|---|
| aleatorio_chaves_grandes | 361.64 | 6.36 | 6.19 | 5.01 | estoura* | **1.64** | 1.84 | base | base | 0.209 ms (11.3%) |
| faixa_estreita | 338.85 | 6.21 | 2.25 | 2.23 | **0.24** | 0.33 | 0.43 | contagem | contagem | 0.207 ms (47.8%) |
| quase_ordenado | **0.34** | 4.27 | 6.04 | 5.01 | estoura* | 1.49 | 0.43 | insercao | insercao | 0.086 ms (20.1%) |
| lista_minuscula | **3.11** | 9.97 | 8.94 | 3.14 | estoura* | 109.56 | 3.25 | insercao | insercao | 0.114 ms (3.5%) |
| **total** | 703.94 | 26.81 | 23.43 | 15.39 | não roda | 113.01 | 5.95 | | | |

## Cenário de erro

| cenário | insercao | intercalacao | rapida | hibrida | contagem | base | ordenar | escolhido | melhor fixo | custo do escolher |
|---|---|---|---|---|---|---|---|---|---|---|
| metades_trocadas | 359.92 | 4.28 | 6.58 | 5.48 | 0.74 | **0.69** | 359.52 | insercao | base | 0.086 ms (0.0%) |
