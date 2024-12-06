import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import buscar_clima


def test_buscar_clima():
    # Testar com uma cidade válida
    resultado = buscar_clima('São Paulo')
    assert 'Clima' in resultado

    # Testar com uma cidade inválida
    resultado = buscar_clima('CidadeInexistente')
    assert 'Erro' in resultado
