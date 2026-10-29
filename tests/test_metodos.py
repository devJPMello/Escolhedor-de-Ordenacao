import random
import unittest

from ordenacao import METODOS, ordenar
from ordenacao.metodos import LIMITE_FAIXA_CONTAGEM, contagem

TODOS = {**METODOS, "ordenar": ordenar}

CASOS = {
    "vazia": [],
    "um_elemento": [42],
    "todos_iguais": [7] * 200,
    "ja_ordenada": list(range(300)),
    "invertida": list(range(300, 0, -1)),
    "negativos": [-5, 3, -1, 0, -100, 99, -5, 2, -3, 1] * 20,
    "so_negativos": list(range(-1, -301, -1)),
    "dois_elementos": [2, 1],
}


class TestMetodos(unittest.TestCase):
    def test_casos_de_borda(self):
        for nome_m, f in TODOS.items():
            for nome_c, v in CASOS.items():
                with self.subTest(metodo=nome_m, caso=nome_c):
                    copia = list(v)
                    self.assertEqual(f(v), sorted(v))
                    self.assertEqual(v, copia, "a entrada não pode ser alterada")

    def test_aleatorias(self):
        rng = random.Random(123)
        for n in (2, 3, 17, 33, 100, 1000):
            for faixa in (3, 1000, 10**12):
                v = [rng.randint(-faixa, faixa) for _ in range(n)]
                for nome_m, f in TODOS.items():
                    if nome_m == "contagem" and 2 * faixa + 1 > LIMITE_FAIXA_CONTAGEM:
                        continue
                    with self.subTest(metodo=nome_m, n=n, faixa=faixa):
                        self.assertEqual(f(v), sorted(v))

    def test_comparativos_aceitam_floats(self):
        v = [3.5, -1.25, 0.0, 2.0, -7.75] * 10
        for nome in ("insercao", "intercalacao", "rapida", "hibrida"):
            with self.subTest(metodo=nome):
                self.assertEqual(METODOS[nome](v), sorted(v))
        self.assertEqual(ordenar(v), sorted(v))

    def test_contagem_recusa_faixa_enorme(self):
        with self.assertRaises(MemoryError):
            contagem([0, LIMITE_FAIXA_CONTAGEM + 10])


if __name__ == "__main__":
    unittest.main()
