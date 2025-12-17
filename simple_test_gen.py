
import os
from dotenv import load_dotenv
from openai import OpenAI

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializar o cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Gerando imagem de teste...")

try:
    response = client.images.generate(
        model="dall-e-3",
        prompt="A cute unicorn in a magical forest, pixel art style",
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    print("\nSucesso! Aqui está a URL da sua imagem:")
    print(image_url)

except Exception as e:
    print(f"\nErro ao gerar imagem: {e}")
