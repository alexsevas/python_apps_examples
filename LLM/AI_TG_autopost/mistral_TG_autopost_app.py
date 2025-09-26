# Телеграм-бот для создания постов в Телеграм канал при помощи LLM Mistral

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from mistralai import Mistral

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
bot = Bot(token="") # ⚠️ ИЗМЕНИТЬ ТОКЕН
dp = Dispatcher()

api_key = "" # ⚠️ ИЗМЕНИТЬ ТОКЕН
model = "mistral-large-latest"

client = Mistral(api_key=api_key)


# Хэндлер на команду /start ---------------------------------------------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    channel_id =  # ЗАМЕНИТЬ НА ВАШ ID КАНАЛА

    while True:
        chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "system",
                "content": "ты ведешь Телеграм канал. Пиши посты о том, что просит пользователь без лишней информации",
            },
            {
                "role": "user",
                "content": "напиши смешную шутку про программистов",
            },
            ]
        )

        await bot.send_message(channel_id, chat_response.choices[0].message.content, parse_mode = "Markdown")

        await asyncio.sleep(10)



# Запуск процесса поллинга новых апдейтов
async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())