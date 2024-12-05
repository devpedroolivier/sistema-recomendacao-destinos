from flask import Flask, render_template, request
from amadeus_integration.flight_search import buscar_voos
import sqlite3
import requests

app = Flask(__name__)

# Função para filtrar destinos com base nos filtros dinâmicos
def filtrar_destinos(orçamento_min=None, orçamento_max=None, categorias=None, meses=None):
    conn = sqlite3.connect('destinos.db')
    cursor = conn.cursor()

    # Início da consulta SQL
    query = '''
    SELECT destino, categoria, orcamento_medio, atividades, melhor_epoca, imagem_url
    FROM destinos
    WHERE 1=1
    '''
    params = []

    # Adicionar filtros dinamicamente
    if orçamento_min is not None and orçamento_max is not None:
        query += " AND orcamento_medio BETWEEN ? AND ?"
        params.extend([orçamento_min, orçamento_max])
    
    if categorias:
        categorias_query = " OR ".join(["LOWER(categoria) LIKE ?" for _ in categorias])
        query += f" AND ({categorias_query})"
        params.extend([f"%{categoria}%" for categoria in categorias])
    
    if meses:
        meses_query = " OR ".join(["LOWER(melhor_epoca) LIKE ?" for _ in meses])
        query += f" AND ({meses_query})"
        params.extend([f"%{mes}%" for mes in meses])

    # Executar a consulta
    print("Consulta SQL:", query)
    print("Parâmetros:", params)
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        return None, "Nenhum destino encontrado com os critérios fornecidos. Tente ajustar os filtros."
    return resultados, None

# Função para buscar clima
def buscar_clima(cidade):
    api_key = "bb5df2b3e0cea0ffd2cb8900903ee6da"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric&lang=pt_br"
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        if resposta.status_code == 200:
            descricao = dados['weather'][0]['description']
            temperatura = dados['main']['temp']
            return f"Clima: {descricao.capitalize()}, {temperatura}°C"
        else:
            return f"Erro na API: {dados.get('message', 'Erro desconhecido')}."
    except Exception as e:
        return f"Erro ao buscar clima: {e}"

# Rota principal para o formulário
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar os dados do formulário
@app.route('/resultados', methods=['POST'])
def resultados():
    # Obter dados do formulário
    orçamento_min = request.form.get('orçamento_min')
    orçamento_max = request.form.get('orçamento_max')
    categorias = request.form.getlist('categorias')  # Obter categorias marcadas
    meses = request.form.getlist('meses')  # Obter meses selecionados

    # Converter orçamento para int apenas se for preenchido
    orçamento_min = int(orçamento_min) if orçamento_min else None
    orçamento_max = int(orçamento_max) if orçamento_max else None

    # Filtrar destinos
    destinos_recomendados, erro = filtrar_destinos(
        orçamento_min=orçamento_min,
        orçamento_max=orçamento_max,
        categorias=categorias if categorias else None,
        meses=meses if meses else None
    )

    if erro:
        return render_template('resultados.html', erro=erro)

    resultados = []
    for destino in destinos_recomendados:
        resultados.append({
            'Destino': destino[0],
            'Categoria': destino[1],
            'Orçamento Médio': destino[2],
            'Atividades': destino[3],
            'Melhor Época': destino[4],
            'Clima': buscar_clima(destino[0]),  # Buscar clima usando o nome do destino
            'imagem_url': destino[5] or '/static/images/default.jpg'  # Usar fallback se necessário
        })

    return render_template('resultados.html', resultados=resultados)

# Rota para a página de busca de voos
@app.route('/buscar-voos')
def buscar_voos_form():
    return render_template('buscar_voos.html')

# Rota para processar a busca de voos
@app.route('/resultados-voos', methods=['POST'])
def resultados_voos():
    origem = request.form.get('origem')  # Código IATA do aeroporto de origem
    destino = request.form.get('destino')  # Código IATA do aeroporto de destino
    data_partida = request.form.get('data_partida')  # Data de partida

    # Chamar a função de busca de voos
    resultados = buscar_voos(origem, destino, data_partida)

    if isinstance(resultados, list):
        return render_template('resultados_voos.html', voos=resultados)
    else:
        # Caso ocorra um erro, exibir a mensagem de erro
        return render_template('resultados_voos.html', erro=resultados)

if __name__ == '__main__':
    app.run(debug=True)
