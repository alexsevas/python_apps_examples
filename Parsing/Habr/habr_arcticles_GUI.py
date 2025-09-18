# conda activate xtts2

# pip install requests beautifulsoup4 PyQt5

'''
GUI-парсер (на PyQt5) habr.ru:
- Позволяет выбрать хаб (ввод URL вручную или из списка популярных)
- Включить/выключить пагинацию (парсить все страницы или только первую)
- Показывает результаты в таблице: название, ссылка, автор, дата
- Сохраняет результат в CSV: articles_YYYY-MM-DD_HH-MM-SS.csv
'''

import sys
import csv
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QCheckBox, QMessageBox, QFileDialog, QHeaderView, QComboBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class HabrParserThread(QThread):
    # Сигналы для передачи данных в GUI
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, base_url, paginate):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.paginate = paginate
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

    def run(self):
        try:
            articles = self.parse_hub(self.base_url, self.paginate)
            self.finished.emit(articles)
        except Exception as e:
            self.error.emit(str(e))

    def get_page_articles(self, url):
        """Парсит одну страницу хаба и возвращает список статей"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.progress.emit(f"Ошибка загрузки {url}: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', {'class': lambda x: x and 'tm-articles-list__item' in x})

        page_articles = []

        for article in articles:
            # Заголовок и ссылка
            title_tag = article.find('a', class_='tm-title__link')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            relative_url = title_tag['href']
            full_url = urljoin("https://habr.com", relative_url)

            # Автор
            author_tag = article.find('a', class_='tm-user-info__username')
            author = author_tag.get_text(strip=True) if author_tag else "Неизвестен"

            # Дата
            time_tag = article.find('time')
            pub_date = time_tag['datetime'] if time_tag and time_tag.get('datetime') else "Неизвестна"

            page_articles.append({
                'title': title,
                'url': full_url,
                'author': author,
                'date': pub_date
            })

        return page_articles

    def get_next_page_url(self, current_url, soup):
        """Находит ссылку на следующую страницу, если есть"""
        next_button = soup.find('a', class_='tm-pagination__page', attrs={'rel': 'next'})
        if not next_button or not next_button.get('href'):
            return None

        next_relative = next_button['href']
        next_url = urljoin("https://habr.com", next_relative)
        return next_url

    def parse_hub(self, start_url, paginate):
        """Основной метод парсинга хаба"""
        all_articles = []
        current_url = start_url
        page_num = 1

        while current_url:
            self.progress.emit(f"Парсинг страницы {page_num}: {current_url}")
            articles = self.get_page_articles(current_url)
            all_articles.extend(articles)

            if not paginate:
                break  # Только первая страница

            # Переход на следующую страницу
            try:
                response = requests.get(current_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                next_url = self.get_next_page_url(current_url, soup)
                if not next_url or next_url == current_url:
                    break
                current_url = next_url
                page_num += 1
                time.sleep(0.5)  # Пауза, чтобы не грузить сервер
            except Exception:
                break

        return all_articles


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Habr Парсер Хабов")
        self.setGeometry(100, 100, 1000, 600)

        self.articles = []

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Выбор хаба
        hub_layout = QHBoxLayout()
        hub_label = QLabel("URL хаба:")
        self.hub_combo = QComboBox()
        self.hub_combo.setEditable(True)
        popular_hubs = [
            "https://habr.com/ru/hubs/python/articles/",
            "https://habr.com/ru/hubs/machine_learning/articles/",
            "https://habr.com/ru/hubs/programming/articles/",
            "https://habr.com/ru/hubs/web/articles/",
            "https://habr.com/ru/hubs/javascript/articles/",
        ]
        self.hub_combo.addItems(popular_hubs)
        hub_layout.addWidget(hub_label)
        hub_layout.addWidget(self.hub_combo, 1)

        # Чекбокс пагинации
        self.paginate_checkbox = QCheckBox("Парсить все страницы")
        self.paginate_checkbox.setChecked(True)
        hub_layout.addWidget(self.paginate_checkbox)

        layout.addLayout(hub_layout)

        # Кнопка запуска
        self.start_button = QPushButton("Запустить парсинг")
        self.start_button.clicked.connect(self.start_parsing)
        layout.addWidget(self.start_button)

        # Статус
        self.status_label = QLabel("Готов к парсингу")
        layout.addWidget(self.status_label)

        # Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Название статьи", "Ссылка", "Автор", "Дата"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table, 1)

        # Кнопка сохранения
        self.save_button = QPushButton("Сохранить в CSV")
        self.save_button.clicked.connect(self.save_to_csv)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)

    def start_parsing(self):
        url = self.hub_combo.currentText().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите URL хаба!")
            return

        # Очищаем предыдущие данные
        self.articles = []
        self.table.setRowCount(0)
        self.save_button.setEnabled(False)
        self.status_label.setText("Парсинг...")

        # Запускаем парсер в отдельном потоке
        self.parser_thread = HabrParserThread(url, self.paginate_checkbox.isChecked())
        self.parser_thread.finished.connect(self.on_parsing_finished)
        self.parser_thread.error.connect(self.on_parsing_error)
        self.parser_thread.progress.connect(self.status_label.setText)
        self.parser_thread.start()

    def on_parsing_finished(self, articles):
        self.articles = articles
        self.display_articles()
        self.status_label.setText(f"Готово! Найдено {len(articles)} статей.")
        self.save_button.setEnabled(True)

    def on_parsing_error(self, error_msg):
        QMessageBox.critical(self, "Ошибка", f"Ошибка парсинга:\n{error_msg}")
        self.status_label.setText("Ошибка!")

    def display_articles(self):
        self.table.setRowCount(len(self.articles))
        for row, article in enumerate(self.articles):
            self.table.setItem(row, 0, QTableWidgetItem(article['title']))
            self.table.setItem(row, 1, QTableWidgetItem(article['url']))
            self.table.setItem(row, 2, QTableWidgetItem(article['author']))
            self.table.setItem(row, 3, QTableWidgetItem(article['date']))

    def save_to_csv(self):
        if not self.articles:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"articles_{timestamp}.csv"

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить как CSV",
            filename,
            "CSV Files (*.csv);;All Files (*)",
            options=options
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['title', 'url', 'author', 'date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for article in self.articles:
                    writer.writerow(article)

            QMessageBox.information(self, "Успех", f"Данные успешно сохранены в:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())