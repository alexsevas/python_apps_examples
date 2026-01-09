# Python-библиотека для скачивания чатов и сообщений с платформ (YouTube, Twitch, Zoom, Facebook)
# pip install chat-downloader

from chat_downloader import ChatDownloader
chat = ChatDownloader().get_chat('https://www.youtube.com/watch?v=_________')
for message in chat:
    print(message['message'])
