# Код демонстрирует создание простого чат-бота, который использует TF-IDF для анализа текста и поиска наиболее подходящего
# ответа на пользовательский запрос.
# Бот векторизует входные данные и вычисляет косинусное сходство, чтобы выбрать лучший ответ из списка заранее заданных фраз.
# Подобный подход может быть полезен в службах поддержки клиентов и для автоматизации простых текстовых взаимодействий.


import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

nltk.download('punkt')

class SimpleChatBot:
    def __init__(self, responses):
        self.responses = responses
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform(self.responses)

    def get_response(self, user_input):
        # Векторизация пользовательского ввода
        user_tfidf = self.vectorizer.transform()

        # Вычисление косинусного сходства
        similarities = cosine_similarity(user_tfidf, self.tfidf_matrix)

        # Выбор наилучшего ответа
        best_match_idx = np.argmax(similarities, axis=1)
        return self.responses[best_match_idx[0]]

# Пример использования
responses = [
    "Привет! Как я могу помочь?",
    "Я могу ответить на ваши вопросы.",
    "Извините, я не понимаю ваш запрос.",
    "Спасибо за обращение!"
]

chat_bot = SimpleChatBot(responses)
user_input = "Как вы можете помочь?"
response = chat_bot.get_response(user_input)
print("Бот:", response)
