import sqlite3

# Conexão com o banco de dados
conn = sqlite3.connect('destinos.db')
cursor = conn.cursor()

# Dados dos destinos
dados_destinos = [
    ("Berlim", "Cultura", 4000, "Museus, História, Vida Noturna", "Mai-Ago", "/static/images/berlim.jpg"),
    ("Buenos Aires", "Compras", 2000, "Shoppings, Gastronomia, Tango", "Out-Mar", "/static/images/buenos_aires.jpg"),
    ("Cancun", "Praia", 3000, "Resorts, Praias, Vida Noturna", "Abr-Jul", "/static/images/cancun.jpg"),
    ("Dubai", "Compras", 6000, "Shopping, Deserto, Luxo", "Out-Abr", "/static/images/dubai.jpg"),
    ("Florianópolis", "Praia", 1200, "Praias, Trilhas, Gastronomia", "Dez-Mar", "/static/images/florianopolis.jpg"),
    ("Honolulu", "Praia", 6000, "Surf, Praias, Trilhas", "Ago-Nov", "/static/images/honolulu.jpg"),
    ("Lisboa", "Cultura", 3500, "Castelos, Vinhos, Gastronomia", "Set-Nov", "/static/images/lisboa.jpg"),
    ("Nova York", "Cultura", 7000, "Times Square, Broadway, Central Park", "Set-Dez", "/static/images/nova_york.jpg"),
    ("Paris", "Cultura", 5000, "Torre Eiffel, Museus, Gastronomia", "Abr-Out", "/static/images/paris.jpg"),
    ("Rio de Janeiro", "Praia", 1500, "Praias, Cristo Redentor, Pão de Açúcar", "Nov-Mar", "/static/images/rio_de_janeiro.jpg"),
    ("Salvador", "Praia", 1000, "Praias, Pelourinho, Comidas Típicas", "Dez-Mar", "/static/images/salvador.jpg"),
    ("Tóquio", "Compras", 8000, "Tecnologia, Cultura Pop, Gastronomia", "Mar-Jun", "/static/images/tóquio.jpg"),
    ("Veneza", "Cultura", 4500, "Passeios de Gôndola, História", "Abr-Jun", "/static/images/veneza.jpg"),
]

# Inserir dados no banco
cursor.executemany("""
INSERT INTO destinos (destino, categoria, orcamento_medio, atividades, melhor_epoca, imagem_url)
VALUES (?, ?, ?, ?, ?, ?)
""", dados_destinos)

# Salvar e fechar conexão
conn.commit()
conn.close()

print("Dados adicionados com sucesso!")
