import os
import requests

# Sua API Key do Pixabay
API_KEY = "47474430-3bc6e099768f77a5f2f6b9e69"

# Lista de destinos para buscar imagens
destinos = [
    "Rio de Janeiro", "Paris", "Dubai", "Florianópolis", "Nova York",
    "Salvador", "Berlim", "Lisboa", "Buenos Aires", "Cancún",
    "Tóquio", "Veneza", "Honolulu"
]

# Caminho para salvar as imagens
caminho_pasta = "static/images"

# Criar a pasta se não existir
os.makedirs(caminho_pasta, exist_ok=True)

# Função para buscar e baixar imagens
def baixar_imagem(destino):
    url = f"https://pixabay.com/api/?key={API_KEY}&q={destino}&image_type=photo&per_page=3"
    try:
        response = requests.get(url)
        data = response.json()
        if "hits" in data and len(data["hits"]) > 0:
            # Pega a primeira imagem retornada
            imagem_url = data["hits"][0]["largeImageURL"]
            response_imagem = requests.get(imagem_url)
            if response_imagem.status_code == 200:
                # Salva a imagem no diretório
                nome_arquivo = f"{destino.replace(' ', '_').lower()}.jpg"
                caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
                with open(caminho_arquivo, "wb") as f:
                    f.write(response_imagem.content)
                print(f"Imagem de {destino} salva em {caminho_arquivo}")
            else:
                print(f"Erro ao baixar a imagem de {destino}. Código HTTP: {response_imagem.status_code}")
        else:
            print(f"Nenhuma imagem encontrada para {destino}.")
    except Exception as e:
        print(f"Erro ao processar {destino}: {e}")

# Processar todos os destinos
for destino in destinos:
    baixar_imagem(destino)
