from amadeus import ResponseError
from flask import Flask, render_template, request
from amadeus_integration.auth import autenticar
from amadeus_integration.flight_search import buscar_voos
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)

def get_iata_code(city_name):
    # Primeiro, verificar no banco de dados local
    codigo_iata = buscar_codigo_iata(city_name)
    if codigo_iata:
        return codigo_iata

    # Caso não encontre, usar a API
    api_key = "6d84f9b22da147a7b13ccf7b05c583c3"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city_name}&key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data['results']:
            for result in data['results']:
                components = result.get('components', {})
                if 'iata' in components:
                    codigo_iata = components['iata']
                    # Salvar no banco de dados
                    salvar_codigo_iata(city_name, codigo_iata)
                    return codigo_iata
        return None
    except Exception as e:
        print(f"Erro na chamada da API: {e}")
        return None

def salvar_codigo_iata(cidade, codigo_iata):
    conn = sqlite3.connect('destinos.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cidades (cidade, codigo_iata) VALUES (?, ?)", (cidade.lower(), codigo_iata))
    conn.commit()
    conn.close()


def buscar_codigo_iata(cidade):
    conn = sqlite3.connect('destinos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT codigo_iata FROM cidades WHERE LOWER(cidade) = ?", (cidade.lower(),))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

# Função para formatar datetime
def datetimeformat(value):
    try:
        date_object = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        return date_object.strftime("%d/%m/%Y às %H:%M")
    except ValueError:
        return value  # Retorna como está se não conseguir formatar

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

# Adicionar o filtro ao Jinja2
app.jinja_env.filters['datetimeformat'] = datetimeformat


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar-destinos')
def buscar_destinos_form():
    return render_template('buscar_destinos.html')

@app.route('/resultados', methods=['POST'])
def resultados():
    orçamento_min = request.form.get('orçamento_min')
    orçamento_max = request.form.get('orçamento_max')
    categorias = request.form.getlist('categorias')
    meses = request.form.getlist('meses')

    orçamento_min = int(orçamento_min) if orçamento_min else None
    orçamento_max = int(orçamento_max) if orçamento_max else None

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
            'Clima': buscar_clima(destino[0]),
            'imagem_url': destino[5] or '/static/images/default.jpg'
        })

    return render_template('resultados.html', resultados=resultados)

@app.route('/buscar-voos')
def buscar_voos_form():
    return render_template('buscar_voos.html')

@app.route('/resultados-voos', methods=['POST'])
def resultados_voos():
    origem = request.form.get('origem')
    destino = request.form.get('destino')
    data_partida = request.form.get('data_partida')

    origem_iata = get_iata_code(origem)
    destino_iata = get_iata_code(destino)

    if not origem_iata:
        erro = f"Não foi possível encontrar o código IATA para a origem: {origem}."
        return render_template('resultados_voos.html', erro=erro)

    if not destino_iata:
        erro = f"Não foi possível encontrar o código IATA para o destino: {destino}."
        return render_template('resultados_voos.html', erro=erro)

    resultados = buscar_voos(origem_iata, destino_iata, data_partida)

    if isinstance(resultados, list):
        return render_template('resultados_voos.html', voos=resultados)
    else:
        return render_template('resultados_voos.html', erro=resultados)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

if __name__ == '__main__':
    app.run(debug=True)
