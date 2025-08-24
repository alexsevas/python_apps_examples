# conda activate allpy311

# python psw_generator.py --length 25

'''
Простой и эффективный скрипт, который создаёт криптографически безопасный пароль заданной длины.
Использует стандартный secrets модуль для максимальной случайности.

Возможности скрипта:
- Генерирует пароль, используя буквы (все регистры), цифры и спецсимволы
- Криптографически стойкий — идеально подходит для безопасных паролей
- Простая CLI: указываешь длину — получаешь новый пароль на выходе

Модули: secrets, string, argparse
'''

import secrets
import string
import argparse

def generate_password(length):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # можно исключить потенциально проблемные символы вроде '\' или '"' по желанию
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Secure Password Generator")
    parser.add_argument("--length", type=int, default=12, help="Password length")
    args = parser.parse_args()
    pwd = generate_password(args.length)
    print(pwd)
