# SMTP — это протокол для отправки почты.
# В Python за него отвечает стандартный модуль smtplib, ничего ставить не нужно.
# Простейший пример: отправка текстового письма через SMTP-сервер:


import smtplib

smtp_server = "smtp.gmail.com"
smtp_port = 587

sender_email = "you@example.com"
password = "your_app_password"
receiver_email = "friend@example.com"

message = """\
From: you@example.com
To: friend@example.com
Subject: Test email from Python

Hello! This is a test email sent via smtplib.
"""

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()  # шифруем соединение
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
