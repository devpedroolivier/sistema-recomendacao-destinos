import sys
import os
from amadeus import ResponseError

# Adicionar o caminho do módulo de autenticação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from amadeus_integration.auth import autenticar


def formatar_duracao(duracao):
    """
    Converte a duração no formato ISO8601 (PT10H25M) para um formato legível (10h 25m).
    """
    duracao = duracao.replace("PT", "").replace("H", "h ").replace("M", "m")
    return duracao.strip()


def buscar_voos(origem, destino, data_partida):
    """
    Função para buscar voos utilizando a API Amadeus.
    :param origem: Código IATA do aeroporto de origem (ex: GRU).
    :param destino: Código IATA do aeroporto de destino (ex: JFK).
    :param data_partida: Data de partida no formato YYYY-MM-DD.
    :return: Lista de voos formatados ou mensagem de erro.
    """
    amadeus = autenticar()
    if not amadeus:
        return "Erro na autenticação. Não foi possível buscar voos."

    try:
        # Chamada para a API Amadeus
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origem,
            destinationLocationCode=destino,
            departureDate=data_partida,
            adults=1,
            max=5
        )

        resultados = response.data
        if not resultados:
            return "Nenhum voo encontrado com os critérios fornecidos."

        # Formatar resultados
        voos_formatados = []
        for voo in resultados:
            detalhes_voo = {
                "id": voo["id"],
                "preco": voo["price"]["total"],
                "moeda": voo["price"]["currency"],
                "duracao_total": formatar_duracao(voo["itineraries"][0]["duration"]),
                "segmentos": []
            }
            for segmento in voo["itineraries"][0]["segments"]:
                detalhes_voo["segmentos"].append({
                    "partida": segmento["departure"]["iataCode"],
                    "chegada": segmento["arrival"]["iataCode"],
                    "horario_partida": segmento["departure"]["at"],
                    "horario_chegada": segmento["arrival"]["at"],
                    "companhia": segmento["carrierCode"],
                    "duracao": formatar_duracao(segmento["duration"]),
                    "paradas": segmento.get("numberOfStops", 0),
                })
            voos_formatados.append(detalhes_voo)

        return voos_formatados

    except ResponseError as error:
        return f"Erro ao buscar voos: {error}"


# Testar a função
if __name__ == "__main__":
    origem = "GRU"  # Aeroporto Internacional de São Paulo
    destino = "JFK"  # Aeroporto Internacional John F. Kennedy
    data_partida = "2024-12-20"  # Data de partida

    resultados = buscar_voos(origem, destino, data_partida)
    if isinstance(resultados, list):
        print("Voos encontrados:\n")
        for voo in resultados:
            print(f"ID da oferta: {voo['id']}")
            print(f"Preço: {voo['preco']} {voo['moeda']}")
            print(f"Duração total: {voo['duracao_total']}")
            print("Segmentos:")
            for segmento in voo["segmentos"]:
                print(f"- {segmento['partida']} -> {segmento['chegada']}")
                print(f"  Horário: {segmento['horario_partida']} -> {segmento['horario_chegada']}")
                print(f"  Companhia: {segmento['companhia']}")
                print(f"  Duração: {segmento['duracao']}")
                print(f"  Paradas: {segmento['paradas']}\n")
    else:
        print(resultados)
