# Mimesis — генератор фейковых данных: имена, email, адреса и телефоны.
# Есть настройка локации, позволяющая выбрать страну и данные будут сгенерированы в соответствии с выбором
# pip install mimesis


from typing import Dict
from mimesis.enums import Gender
from mimesis import Person

def generate_fake_user(locale: str = "es", gender: Gender = Gender.MALE) -> Dict[str, str]:
    """
    Генерирует фейковые пользовательские данные на основе локали и пола.

    :param locale: Локаль (например, 'ru', 'en', 'es')
    :param gender: Пол (Gender.MALE или Gender.FEMALE)
    :return: Словарь с фейковыми данными пользователя
    """
    person = Person(locale)

    user_data = {
        "name": person.full_name(gender=gender),
        "height": person.height(),
        "phone": person.telephone(),
        "occupation": person.occupation(),
    }

    return user_data

if __name__ == "__main__":
    fake_user = generate_fake_user(locale="ru", gender=Gender.MALE)
    print(fake_user)
