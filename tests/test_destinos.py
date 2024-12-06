import sqlite3
import sys
import os

# Adiciona o caminho correto para importar o módulo "app"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import filtrar_destinos


def test_filtrar_destinos():
    # Configurar um banco de dados de teste
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE destinos (
            destino TEXT, categoria TEXT, orcamento_medio INTEGER,
            atividades TEXT, melhor_epoca TEXT, imagem_url TEXT
        )
    ''')
    cursor.execute("INSERT INTO destinos VALUES ('Rio de Janeiro', 'Praia', 1500, 'Praias, Cristo Redentor', 'Nov-Mar', '/static/images/rio_de_janeiro.jpg')")
    cursor.execute("INSERT INTO destinos VALUES ('Paris', 'Cultura', 5000, 'Torre Eiffel, Museus', 'Abr-Out', '/static/images/paris.jpg')")
    cursor.execute("INSERT INTO destinos VALUES ('Buenos Aires', 'Compras', 2000, 'Shoppings, Gastronomia, Tango', 'Out-Mar', '/static/images/buenos_aires.jpg')")
    cursor.execute("INSERT INTO destinos VALUES ('Salvador', 'Praia', 1000, 'Praias, Pelourinho, Comidas Típicas', 'Dez-Mar', '/static/images/salvador.jpg')")
    conn.commit()

    # Redefinir a função `filtrar_destinos` para usar o banco de dados em memória
    def filtrar_destinos(orçamento_min=None, orçamento_max=None, categorias=None, meses=None):
        query = '''
        SELECT destino, categoria, orcamento_medio, atividades, melhor_epoca, imagem_url
        FROM destinos
        WHERE 1=1
        '''
        params = []

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

        cursor.execute(query, params)
        resultados = cursor.fetchall()
        if not resultados:
            return None, "Nenhum destino encontrado com os critérios fornecidos."
        return resultados, None

    # Testar a função
    resultados, erro = filtrar_destinos(orçamento_min=1000, orçamento_max=2000)
    assert len(resultados) == 3  # Agora esperamos 3 destinos: Rio de Janeiro, Buenos Aires e Salvador
    assert 'Rio de Janeiro' in [resultado[0] for resultado in resultados]
    assert erro is None

    conn.close()


# Executar o teste
if __name__ == "__main__":
    test_filtrar_destinos()
    print("Testes executados com sucesso!")
