# Реальные письма состоят из заголовков и тела, часто в нескольких форматах (текст + HTML). Удобнее собирать их через email-модуль.
# Здесь send_message() принимает уже готовый объект письма, а не строку.


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_server = "smtp.gmail.com"
smtp_port = 587

sender_email = "you@example.com"
password = "your_app_password"
receiver_email = "friend@example.com"

msg = MIMEMultipart("alternative")
msg["Subject"] = "Report from Python script"
msg["From"] = sender_email
msg["To"] = receiver_email

text_part = """\
Hi!
Here is your daily report in plain text.
"""

html_part = """\
<html>
  <body>
    <h2>Daily report</h2>
    <p>This is a <b>HTML</b> version of the email.</p>
  </body>
</html>
"""

msg.attach(MIMEText(text_part, "plain"))
msg.attach(MIMEText(html_part, "html"))

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(sender_email, password)
    server.send_message(msg)