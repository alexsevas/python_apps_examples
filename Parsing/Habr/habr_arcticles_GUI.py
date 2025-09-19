# conda activate xtts2

# pip install requests beautifulsoup4 PyQt5

# GUI-парсер (на PyQt5) habr.ru


import sys
import csv
import time
import re
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QCheckBox, QMessageBox, QFileDialog, QHeaderView, QComboBox,
    QSpinBox, QGroupBox, QFormLayout, QProgressBar, QStatusBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class HabrParserThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str, int, int)
    page_parsed = pyqtSignal(list, int)
    total_pages_detected = pyqtSignal(int)

    def __init__(self, base_url, max_pages):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.max_pages = max_pages
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        self.articles_global_index = 0

    def run(self):
        try:
            first_page_articles, total_pages = self.parse_first_page()
            self.total_pages_detected.emit(total_pages)

            if self.max_pages > total_pages:
                self.max_pages = total_pages

            for article in first_page_articles:
                self.articles_global_index += 1
                article['global_index'] = self.articles_global_index
            self.page_parsed.emit(first_page_articles, 1)

            for page_num in range(2, self.max_pages + 1):
                if self.isInterruptionRequested():
                    break

                self.progress.emit(f"Парсинг страницы {page_num} из {self.max_pages}...", page_num, self.max_pages)
                articles = self.parse_page(page_num)
                for article in articles:
                    self.articles_global_index += 1
                    article['global_index'] = self.articles_global_index
                self.page_parsed.emit(articles, page_num)
                time.sleep(0.3)

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def parse_first_page(self):
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            total_pages = self.get_total_pages(soup)
            articles = self.extract_articles(soup)
            return articles, total_pages
        except Exception:
            return [], 1

    def get_total_pages(self, soup):
        pagination = soup.find('div', class_='tm-pagination')
        if not pagination:
            return 1

        page_links = pagination.find_all('a', class_='tm-pagination__page')
        page_numbers = []
        for link in page_links:
            text = link.get_text(strip=True)
            if text.isdigit():
                page_numbers.append(int(text))

        return max(page_numbers) if page_numbers else 1

    def parse_page(self, page_num):
        if page_num == 1:
            url = self.base_url
        else:
            base = self.base_url.rstrip('/')
            if '/page' in base:
                base = base[:base.rfind('/page')]
            url = f"{base}/page{page_num}/"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return self.extract_articles(soup)
        except Exception:
            return []

    def extract_articles(self, soup):
        articles = soup.find_all('article', {'class': lambda x: x and 'tm-articles-list__item' in x})
        page_articles = []

        for article in articles:
            title_tag = article.find('a', class_='tm-title__link')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            relative_url = title_tag['href']
            full_url = urljoin("https://habr.com", relative_url)

            # 👇 Извлекаем ID статьи из URL
            article_id = "N/A"
            match = re.search(r'/articles/(\d+)/?$', relative_url)
            if match:
                article_id = match.group(1)

            author_tag = article.find('a', class_='tm-user-info__username')
            author = author_tag.get_text(strip=True) if author_tag else "Неизвестен"

            time_tag = article.find('time')
            pub_date = time_tag['datetime'] if time_tag and time_tag.get('datetime') else "Неизвестна"

            page_articles.append({
                'global_index': 0,
                'article_id': article_id,  # 👈 ДОБАВЛЕНО
                'title': title,
                'url': full_url,
                'author': author,
                'date': pub_date
            })

        return page_articles


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Habr Парсер Хабов")
        self.setGeometry(100, 100, 1200, 700)

        self.articles = []
        self.current_page_articles = []

        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        settings_group = QGroupBox("Настройки парсинга")
        settings_layout = QFormLayout()

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
        settings_layout.addRow("URL хаба:", self.hub_combo)

        pagination_layout = QHBoxLayout()
        self.paginate_checkbox = QCheckBox("Пагинация")
        self.paginate_checkbox.setChecked(True)
        self.paginate_checkbox.stateChanged.connect(self.on_paginate_changed)

        self.pages_spin = QSpinBox()
        self.pages_spin.setMinimum(1)
        self.pages_spin.setMaximum(1)
        self.pages_spin.setValue(1)

        pagination_layout.addWidget(self.paginate_checkbox)
        pagination_layout.addWidget(QLabel("Страниц:"))
        pagination_layout.addWidget(self.pages_spin)
        pagination_layout.addStretch()

        settings_layout.addRow("Парсинг:", pagination_layout)
        settings_group.setLayout(settings_layout)
        left_layout.addWidget(settings_group)

        self.start_button = QPushButton("▶️ Запустить парсинг")
        self.start_button.clicked.connect(self.start_parsing)
        left_layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)

        # 👇 Обновлённые заголовки: добавлен "ID"
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["№", "ID", "Название", "Ссылка", "Автор", "Дата"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setSortingEnabled(False)
        left_layout.addWidget(self.table, 1)

        self.save_button = QPushButton("💾 Сохранить в CSV")
        self.save_button.clicked.connect(self.save_to_csv)
        self.save_button.setEnabled(False)
        left_layout.addWidget(self.save_button)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        placeholder = QLabel("Правая панель (можно использовать позже)")
        placeholder.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(placeholder)

        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к парсингу")

    def on_paginate_changed(self, state):
        self.pages_spin.setEnabled(state == Qt.Checked)

    def start_parsing(self):
        url = self.hub_combo.currentText().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите URL хаба!")
            return

        max_pages = self.pages_spin.value() if self.paginate_checkbox.isChecked() else 1

        self.articles = []
        self.table.setRowCount(0)
        self.save_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("⏳ Начинаем парсинг...")

        self.parser_thread = HabrParserThread(url, max_pages)
        self.parser_thread.finished.connect(self.on_parsing_finished)
        self.parser_thread.error.connect(self.on_parsing_error)
        self.parser_thread.progress.connect(self.update_progress)
        self.parser_thread.page_parsed.connect(self.add_articles_to_table)
        self.parser_thread.total_pages_detected.connect(self.update_max_pages)
        self.parser_thread.start()

    def update_max_pages(self, total_pages):
        self.pages_spin.setMaximum(total_pages)
        if self.pages_spin.value() > total_pages:
            self.pages_spin.setValue(total_pages)
        self.status_bar.showMessage(f"Обнаружено {total_pages} страниц. Парсим {self.pages_spin.value()}...")

    def update_progress(self, message, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_bar.showMessage(message)

    def add_articles_to_table(self, articles, page_num):
        current_row = self.table.rowCount()
        self.table.setRowCount(current_row + len(articles))

        for i, article in enumerate(articles):
            row = current_row + i
            # 👇 Обновлённый порядок: добавлено поле ID
            self.table.setItem(row, 0, QTableWidgetItem(str(article['global_index'])))
            self.table.setItem(row, 1, QTableWidgetItem(article['article_id']))
            self.table.setItem(row, 2, QTableWidgetItem(article['title']))
            self.table.setItem(row, 3, QTableWidgetItem(article['url']))
            self.table.setItem(row, 4, QTableWidgetItem(article['author']))
            self.table.setItem(row, 5, QTableWidgetItem(article['date']))

        self.articles.extend(articles)
        self.status_bar.showMessage(f"Добавлено {len(articles)} статей со страницы {page_num}. Всего: {len(self.articles)}")

    def on_parsing_finished(self):
        self.status_bar.showMessage(f"✅ Парсинг завершён! Всего собрано {len(self.articles)} статей.")
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.save_button.setEnabled(True)
        self.table.setSortingEnabled(True)

    def on_parsing_error(self, error_msg):
        QMessageBox.critical(self, "Ошибка", f"Ошибка парсинга:\n{error_msg}")
        self.status_bar.showMessage("❌ Ошибка!")

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
            # 👇 Добавлено поле 'article_id'
            fieldnames = ['global_index', 'article_id', 'title', 'url', 'author', 'date']
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for article in self.articles:
                    writer.writerow(article)

            QMessageBox.information(self, "Успех", f"Данные успешно сохранены в:\n{file_path}")
            self.status_bar.showMessage(f"Файл сохранён: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")
            self.status_bar.showMessage("❌ Ошибка сохранения!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
