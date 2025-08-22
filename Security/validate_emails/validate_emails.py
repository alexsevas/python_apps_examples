# conda activate allpy31

# Проверка валидности email из списка
# Простая проверка списка email на базовый формат. Помогает фильтровать ввод или загружать корректные контакты.
# Без зависимостей, работает на стандартной библиотеке.

import re

EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

def validate_emails(emails):
    valid = [e for e in emails if EMAIL_REGEX.match(e)]
    invalid = [e for e in emails if not EMAIL_REGEX.match(e)]
    return valid, invalid

if __name__ == "__main__":
    sample = ["test@example.com", "bad-email@", "user@domain.org"]
    valid, invalid = validate_emails(sample)
    print(f"✅ Valid: {valid}")
    print(f"❌ Invalid: {invalid}")
