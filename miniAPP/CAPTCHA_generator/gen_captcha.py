# Генерация CAPTCHA

# При желании можно добавить дополнительных эффектов и т.д., чтобы даже ChatGPT не справился


from captcha.image import ImageCaptcha
from PIL import Image
def generate_captcha_text(length):
  import string
  import random
  return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_captcha(captcha_length=7, save_path='CAPTCHA.png'):
  image = ImageCaptcha(width=500, height=100)
  captcha_text = generate_captcha_text(captcha_length)
  data = image.generate(captcha_text)
  image.write(captcha_text, save_path)
  return captcha_text

if __name__ == '__main__':
  captcha_text = generate_captcha()
  print('CAPTCHA text:', captcha_text)

Image.open('CAPTCHA.png')
