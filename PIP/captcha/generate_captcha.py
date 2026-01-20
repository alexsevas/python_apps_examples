# Генерируем капчу:
# - generate_code создаёт случайный набор из букв и цифр.
# - ImageCaptcha рисует картинку с этим кодом.
# - Картинка сохраняется как captcha.png, а правильный код возвращается для дальнейшей проверки.

# pip install captcha


from captcha.image import ImageCaptcha
import random
import string

def generate_code(length: int = 5) -> str:
    symbols = string.ascii_uppercase + string.digits
    return ''.join(random.choice(symbols) for _ in range(length))

def generate_captcha(image_path: str = "captcha.png") -> str:
    image_captcha = ImageCaptcha(width=200, height=80)
    code = generate_code()
    image = image_captcha.generate_image(code)
    image.save(image_path)
    return code

if __name__ == "__main__":
    correct_code = generate_captcha()
    print("Captcha code:", correct_code)
