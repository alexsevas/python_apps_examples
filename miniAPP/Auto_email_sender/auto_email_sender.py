
# Модули: smtplib, email, csv, argparse

# Скрипт, который автоматически отправляет письма по списку адресов из CSV-файла
# Пример использования (CLI):
# python bulk_emailer.py --csv recipients.csv --smtp_host smtp.gmail.com --port 587 --user you@example.com --password ****

import smtplib
import csv
import argparse
from email.message import EmailMessage

def send_bulk(csv_path, smtp_host, port, user, password, dry=False):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with smtplib.SMTP(smtp_host, port) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            for row in reader:
                msg = EmailMessage()
                msg["From"] = user
                msg["To"] = row["email"]
                msg["Subject"] = row["subject"]
                msg.set_content(row["message"])
                if dry:
                    print(f"DRY RUN → To: {row['email']}, Subject: {row['subject']}")
                else:
                    smtp.send_message(msg)
                    print(f"Sent to {row['email']}")

if __name__ == "__main__":
    p = argparse.ArgumentParser("Bulk Email Sender")
    p.add_argument("--csv", required=True, help="CSV file with email,subject,message columns")
    p.add_argument("--smtp_host", default="smtp.gmail.com")
    p.add_argument("--port", type=int, default=587)
    p.add_argument("--user", required=True, help="SMTP username")
    p.add_argument("--password", required=True, help="SMTP password or app-password")
    p.add_argument("--dry", action="store_true", help="Dry run (dont actually send)")
    args = p.parse_args()
    send_bulk(args.csv, args.smtp_host, args.port, args.user, args.password, args.dry)
