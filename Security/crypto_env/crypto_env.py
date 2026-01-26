# Безопасное шифрование конфигураций (.env → .env.enc)
# Храни конфиги и API-ключи безопасно:
# encrypt_env() — зашифровывает .env,
# decrypt_env() — расшифровывает перед запуском.
# Ключ лежит отдельно и не коммитится в git.

# pip install cryptography


from cryptography.fernet import Fernet
import os

def encrypt_env(src=".env", dst=".env.enc", key_file="key.txt"):
    key = Fernet.generate_key()
    with open(key_file, "wb") as f: f.write(key)
    fernet = Fernet(key)
    with open(src, "rb") as f: data = f.read()
    with open(dst, "wb") as f: f.write(fernet.encrypt(data))

def decrypt_env(dst=".env", src=".env.enc", key_file="key.txt"):
    key = open(key_file,"rb").read()
    fernet = Fernet(key)
    with open(src,"rb") as f: data=f.read()
    with open(dst,"wb") as f: f.write(fernet.decrypt(data))