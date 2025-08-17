# conda activate allpy311

# pip install openai python-telegram-bot

'''
Минимальный пример кода на Python, демонстрирующий реализацию стриминга ответа от LLM в Telegram в реальном времени.
Используется:
* OpenAI API (через stream=True) для получения ответа частями
* python-telegram-bot для отправки сообщений в Telegram
'''

import openai
import asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройки
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
openai.api_key = OPENAI_API_KEY

# ID чата можно узнать после отправки /start боту
USER_CHAT_ID = 123456789

# Основная функция генерации ответа с потоком
async def stream_response(prompt, bot: Bot, chat_id: int):
    # Отправим пустое сообщение, которое будем редактировать
    msg = await bot.send_message(chat_id=chat_id, text="⌛️ Generating...")
    full_text = ""

    # Запрос к OpenAI с потоковой генерацией
    response = openai.ChatCompletion.create(
        model="gpt-4",  # или gpt-3.5-turbo
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    # Обрабатываем поток
    async for chunk in wrap_stream(response):
        delta = chunk['choices'][0].get('delta', {}).get('content')
        if delta:
            full_text += delta
            # Периодически обновляем сообщение
            if len(full_text) % 20 == 0:
                await msg.edit_text(full_text)

    # Финальное обновление
    await msg.edit_text(full_text)


# Обёртка для OpenAI-стрима (сделаем из генератора асинхронный)
async def wrap_stream(generator):
    loop = asyncio.get_event_loop()
    for chunk in generator:
        yield await loop.run_in_executor(None, lambda: chunk)

# Обработчик команды /ask
async def ask(update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("❗️ Введите текст после /ask")
        return

    await stream_response(prompt, context.bot, update.effective_chat.id)

# Запуск бота
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("ask", ask))
    app.run_polling()

if __name__ == "__main__":
    main()
