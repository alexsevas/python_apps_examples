#conda activate allpy311

from g4f.client import Client

client = Client()
response = client.images.generate(
  model="gemini",
  prompt="a green beautiful cat",
)
image_url = response.data[0].url

print(image_url)