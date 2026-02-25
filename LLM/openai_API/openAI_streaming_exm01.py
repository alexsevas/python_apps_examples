# Пример, как реализовать стриминг из LLM в Telegram с защитой от flood limit с помощью `aiogram`, и объяснение, почему
# `aiogram` лучше для продвинутых Telegram-ботов.
#
# Пример: aiogram + OpenAI Streaming + Flood Control:
# * Полностью async на asyncio — эффективнее и отзывчивее.
# * Легко масштабируется с middlewares, filters, states.
# * Совместим с FastAPI и BackgroundTasks.
# * Безопасен к flood limit через TelegramRetryAfter.

# pip install openai aiogram


import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramRetryAfter
import openai

# Настройки
BOT_TOKEN = "YOUR_TELEGRAM_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_KEY"
openai.api_key = OPENAI_API_KEY

# Логгирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обертка для стриминга OpenAI
async def wrap_stream(generator):
    loop = asyncio.get_event_loop()
    for chunk in generator:
        yield await loop.run_in_executor(None, lambda: chunk)

# Функция безопасного редактирования (борьба с flood)
async def safe_edit(message: Message, text: str):
    try:
        await message.edit_text(text)
    except TelegramRetryAfter as e:
        logging.warning(f"Flood control! Sleep for {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        await safe_edit(message, text)
    except Exception as e:
        logging.warning(f"Unexpected error during edit: {e}")

# Основная логика генерации и стриминга
@dp.message(Command("ask"))
async def handle_ask(message: Message):
    prompt = message.text.replace("/ask", "").strip()
    if not prompt:
        await message.reply("❗️ Пожалуйста, укажи запрос после /ask")
        return

    reply = await message.answer("⌛️ Думаю...")
    full_text = ""
    last_edit = asyncio.get_event_loop().time()

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    async for chunk in wrap_stream(response):
        delta = chunk["choices"][0].get("delta", {}).get("content")
        if delta:
            full_text += delta
            now = asyncio.get_event_loop().time()
            if now - last_edit > 1:
                await safe_edit(reply, full_text)
                last_edit = now

    await safe_edit(reply, full_text)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
