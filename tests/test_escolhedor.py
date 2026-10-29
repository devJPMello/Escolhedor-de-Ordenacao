import random
import unittest

from bench import cenarios
from ordenacao import escolher
from ordenacao.escolhedor import escolher_uma_passada


def nome(v):
    return escolher(v, com_nome=True)[0]


class TestEscolher(unittest.TestCase):
    def test_lista_pequena_vai_para_insercao(self):
        self.assertEqual(nome([]), "insercao")
        self.assertEqual(nome([5]), "insercao")
        self.assertEqual(nome([9, -3, 10**15, 0]), "insercao")

    def test_quase_ordenada_vai_para_insercao(self):
        self.assertEqual(nome(cenarios.quase_ordenado()), "insercao")
        self.assertEqual(nome(list(range(5000))), "insercao")
        self.assertEqual(nome([1] * 5000), "insercao")

    def test_faixa_estreita_vai_para_contagem(self):
        self.assertEqual(nome(cenarios.faixa_estreita()), "contagem")

    def test_negativos_em_faixa_estreita(self):
        rng = random.Random(1)
        v = [rng.randint(-50, 50) for _ in range(1000)]
        self.assertEqual(nome(v), "contagem")

    def test_faixa_enorme_nunca_vai_para_contagem(self):
        rng = random.Random(1)
        v = [rng.randint(0, 10) for _ in range(5000)] + [10**12]
        rng.shuffle(v)
        self.assertNotEqual(nome(v), "contagem")
        # mesmo com n gigante a contagem não pode passar do limite absoluto
        v = [rng.randrange(3_000_000) for _ in range(1_000_000)]
        self.assertNotEqual(nome(v), "contagem")

    def test_chaves_grandes_vao_para_base(self):
        self.assertEqual(nome(cenarios.aleatorio_chaves_grandes()), "base")

    def test_nao_inteiros_nao_vao_para_contagem_nem_base(self):
        rng = random.Random(2)
        v = [rng.random() for _ in range(1000)]
        self.assertEqual(nome(v), "hibrida")
        v = [rng.randint(0, 10) for _ in range(1000)] + [0.5]
        self.assertEqual(nome(v), "hibrida")
        v = ["b", "a", "d", "c"] * 100
        self.assertEqual(nome(v), "hibrida")

    def test_booleanos_nao_vao_para_contagem(self):
        self.assertEqual(nome([True, False] * 100), "hibrida")

    def test_versao_uma_passada_decide_igual(self):
        rng = random.Random(3)
        listas = [cenarios.aleatorio_chaves_grandes(), cenarios.faixa_estreita(),
                  cenarios.quase_ordenado(), [rng.random() for _ in range(500)],
                  list(range(10))]
        for v in listas:
            with self.subTest(n=len(v)):
                self.assertEqual(escolher_uma_passada(v), nome(v))


if __name__ == "__main__":
    unittest.main()
