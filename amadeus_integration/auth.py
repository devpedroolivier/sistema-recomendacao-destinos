from amadeus import Client, ResponseError

def autenticar():
    try:
        amadeus = Client(
            client_id="1mtBPj9KLJFlgK0492U8NEbIp0z8xvVw",
            client_secret="3C0uNRe6GMYXXbvO"
        )
        return amadeus
    except ResponseError as error:
        print(f"Erro ao autenticar: {error}")
        return None


