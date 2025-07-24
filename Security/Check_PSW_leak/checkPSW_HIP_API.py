# conda activate allpy311
# pip install requests

# Проверка паролей на утечку через HaveIBeenPwned API

import hashlib
import requests

def is_password_pwned(password: str) -> bool:
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    res = requests.get(url)
    return any(line.split(':')[0] == suffix for line in res.text.splitlines())

# Пример использования
password = "qwerty"
if is_password_pwned(password):
    print("⚠️ Пароль найден в базе утечек!")
else:
    print("✅ Пароль не найден в утечках.")

'''
Код использует [HaveIBeenPwned API](https://haveibeenpwned.com/API/v3#SearchingPwnedPasswordsByRange) и алгоритм k-Anonymity, 
не передавая сам пароль или полный хеш. Идеально для проверки безопасности паролей на клиенте или при регистрации.
'''
