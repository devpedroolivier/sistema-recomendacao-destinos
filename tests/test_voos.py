import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from amadeus_integration.flight_search import buscar_voos


def test_buscar_voos():
    # Testar com parâmetros válidos
    resultados = buscar_voos(origem="GRU", destino="JFK", data_partida="2024-12-20")
    assert isinstance(resultados, list)
    assert len(resultados) > 0

    # Testar com parâmetros inválidos
    resultados = buscar_voos(origem="INVALID", destino="INVALID", data_partida="2024-12-20")
    assert isinstance(resultados, str)
    assert "Erro" in resultados
