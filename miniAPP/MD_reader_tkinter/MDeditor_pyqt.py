# conda activate allpy311, ...py311test, py310test, py39test
# pip install PyQt5 PyQtWebEngine

import sys
import markdown
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QSplitter, QFileDialog,
                             QAction, QToolBar)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont


class MarkdownViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.init_ui()

    def init_ui(self):
        # Основной виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Создаем сплиттер для разделения окна
        splitter = QSplitter(Qt.Horizontal)

        # Левая панель - редактор
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Courier", 11))
        self.editor.textChanged.connect(self.update_preview)

        # Правая панель - предпросмотр
        self.preview = QWebEngineView()

        # Добавляем виджеты в сплиттер
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)

        # Устанавливаем размеры панелей (50/50)
        splitter.setSizes([500, 500])

        # Основной layout
        layout = QHBoxLayout(main_widget)
        layout.addWidget(splitter)

        # Создаем меню и тулбар
        self.create_menu_bar()
        self.create_toolbar()

        # Устанавливаем заголовок и размеры окна
        self.setWindowTitle('Markdown Viewer & Editor')
        self.setGeometry(100, 100, 1200, 800)

        # Инициализируем предпросмотр
        self.update_preview()

    def create_menu_bar(self):
        # Меню Файл
        file_menu = self.menuBar().addMenu('Файл')

        # Действие: Новый файл
        new_action = QAction('Новый', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        # Действие: Открыть файл
        open_action = QAction('Открыть', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Действие: Сохранить файл
        save_action = QAction('Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        # Действие: Сохранить как
        save_as_action = QAction('Сохранить как', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Кнопки для быстрого доступа
        new_action = QAction('Новый', self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)

        open_action = QAction('Открыть', self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        save_action = QAction('Сохранить', self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

    def new_file(self):
        self.editor.clear()
        self.current_file = None
        self.setWindowTitle('Markdown Viewer & Editor - Новый файл')

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Открыть файл', '', 'Markdown Files (*.md);;All Files (*)'
        )

        if file_name:
            with open(file_name, 'r', encoding='utf-8') as file:
                self.editor.setPlainText(file.read())
            self.current_file = file_name
            self.setWindowTitle(f'Markdown Viewer & Editor - {file_name}')

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self.editor.toPlainText())
        else:
            self.save_file_as()

    def save_file_as(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить файл', '', 'Markdown Files (*.md);;All Files (*)'
        )

        if file_name:
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(self.editor.toPlainText())
            self.current_file = file_name
            self.setWindowTitle(f'Markdown Viewer & Editor - {file_name}')

    def update_preview(self):
        # Получаем текст из редактора
        markdown_text = self.editor.toPlainText()

        # Конвертируем Markdown в HTML
        html = self.markdown_to_html(markdown_text)

        # Отображаем в предпросмотре
        self.preview.setHtml(html)

    def markdown_to_html(self, text):
        # Расширения для поддержки различных элементов Markdown
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br'
        ])

        # Конвертируем Markdown в HTML
        html_body = md.convert(text)

        # Создаем полную HTML страницу с CSS стилями
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 800px;
                    margin: 0 auto;
                    color: #333;
                    background-color: #fff;
                }}

                h1, h2, h3, h4, h5, h6 {{
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                }}

                h1 {{
                    font-size: 2em;
                    border-bottom: 1px solid #eaecef;
                    padding-bottom: 0.3em;
                }}

                h2 {{
                    font-size: 1.5em;
                    border-bottom: 1px solid #eaecef;
                    padding-bottom: 0.3em;
                }}

                p {{
                    margin-top: 0;
                    margin-bottom: 16px;
                }}

                a {{
                    color: #0366d6;
                    text-decoration: none;
                }}

                a:hover {{
                    text-decoration: underline;
                }}

                code {{
                    padding: 0.2em 0.4em;
                    margin: 0;
                    font-size: 85%;
                    background-color: rgba(27,31,35,0.05);
                    border-radius: 3px;
                    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
                }}

                pre {{
                    padding: 16px;
                    overflow: auto;
                    font-size: 85%;
                    line-height: 1.45;
                    background-color: #f6f8fa;
                    border-radius: 3px;
                }}

                pre code {{
                    padding: 0;
                    margin: 0;
                    overflow: visible;
                    font-size: 100%;
                    word-wrap: normal;
                    background-color: transparent;
                    border: 0;
                }}

                blockquote {{
                    padding: 0 1em;
                    color: #6a737d;
                    border-left: 0.25em solid #dfe2e5;
                    margin: 0 0 16px 0;
                }}

                ul, ol {{
                    padding-left: 2em;
                    margin-top: 0;
                    margin-bottom: 16px;
                }}

                li {{
                    margin-bottom: 0.25em;
                }}

                li > p {{
                    margin-top: 16px;
                }}

                table {{
                    display: block;
                    width: 100%;
                    overflow: auto;
                    border-collapse: collapse;
                    margin-bottom: 16px;
                }}

                table th {{
                    font-weight: 600;
                }}

                table th, table td {{
                    padding: 6px 13px;
                    border: 1px solid #dfe2e5;
                }}

                table tr:nth-child(2n) {{
                    background-color: #f6f8fa;
                }}

                img {{
                    max-width: 100%;
                    box-sizing: content-box;
                }}

                hr {{
                    height: 0.25em;
                    padding: 0;
                    margin: 24px 0;
                    background-color: #e1e4e8;
                    border: 0;
                }}

                /* Стили для подсветки синтаксиса */
                .codehilite .hll {{ background-color: #ffffcc }}
                .codehilite  {{ background: #f8f8f8; }}
                .codehilite .c {{ color: #408080; font-style: italic }} /* Comment */
                .codehilite .err {{ border: 1px solid #FF0000 }} /* Error */
                .codehilite .k {{ color: #008000; font-weight: bold }} /* Keyword */
                .codehilite .o {{ color: #666666 }} /* Operator */
                .codehilite .cm {{ color: #408080; font-style: italic }} /* Comment.Multiline */
                .codehilite .cp {{ color: #BC7A00 }} /* Comment.Preproc */
                .codehilite .c1 {{ color: #408080; font-style: italic }} /* Comment.Single */
                .codehilite .cs {{ color: #408080; font-style: italic }} /* Comment.Special */
                .codehilite .gd {{ color: #A00000 }} /* Generic.Deleted */
                .codehilite .ge {{ font-style: italic }} /* Generic.Emph */
                .codehilite .gr {{ color: #FF0000 }} /* Generic.Error */
                .codehilite .gh {{ color: #000080; font-weight: bold }} /* Generic.Heading */
                .codehilite .gi {{ color: #00A000 }} /* Generic.Inserted */
                .codehilite .go {{ color: #888888 }} /* Generic.Output */
                .codehilite .gp {{ color: #000080; font-weight: bold }} /* Generic.Prompt */
                .codehilite .gs {{ font-weight: bold }} /* Generic.Strong */
                .codehilite .gu {{ color: #800080; font-weight: bold }} /* Generic.Subheading */
                .codehilite .gt {{ color: #0044DD }} /* Generic.Traceback */
                .codehilite .kc {{ color: #008000; font-weight: bold }} /* Keyword.Constant */
                .codehilite .kd {{ color: #008000; font-weight: bold }} /* Keyword.Declaration */
                .codehilite .kn {{ color: #008000; font-weight: bold }} /* Keyword.Namespace */
                .codehilite .kp {{ color: #008000 }} /* Keyword.Pseudo */
                .codehilite .kr {{ color: #008000; font-weight: bold }} /* Keyword.Reserved */
                .codehilite .kt {{ color: #B00040 }} /* Keyword.Type */
                .codehilite .m {{ color: #666666 }} /* Literal.Number */
                .codehilite .s {{ color: #BA2121 }} /* Literal.String */
                .codehilite .na {{ color: #7D9029 }} /* Name.Attribute */
                .codehilite .nb {{ color: #008000 }} /* Name.Builtin */
                .codehilite .nc {{ color: #0000FF; font-weight: bold }} /* Name.Class */
                .codehilite .no {{ color: #880000 }} /* Name.Constant */
                .codehilite .nd {{ color: #AA22FF }} /* Name.Decorator */
                .codehilite .ni {{ color: #999999; font-weight: bold }} /* Name.Entity */
                .codehilite .ne {{ color: #D2413A; font-weight: bold }} /* Name.Exception */
                .codehilite .nf {{ color: #0000FF }} /* Name.Function */
                .codehilite .nl {{ color: #A0A000 }} /* Name.Label */
                .codehilite .nn {{ color: #0000FF; font-weight: bold }} /* Name.Namespace */
                .codehilite .nt {{ color: #008000; font-weight: bold }} /* Name.Tag */
                .codehilite .nv {{ color: #19177C }} /* Name.Variable */
                .codehilite .ow {{ color: #AA22FF; font-weight: bold }} /* Operator.Word */
                .codehilite .w {{ color: #bbbbbb }} /* Text.Whitespace */
                .codehilite .mf {{ color: #666666 }} /* Literal.Number.Float */
                .codehilite .mh {{ color: #666666 }} /* Literal.Number.Hex */
                .codehilite .mi {{ color: #666666 }} /* Literal.Number.Integer */
                .codehilite .mo {{ color: #666666 }} /* Literal.Number.Oct */
                .codehilite .sb {{ color: #BA2121 }} /* Literal.String.Backtick */
                .codehilite .sc {{ color: #BA2121 }} /* Literal.String.Char */
                .codehilite .sd {{ color: #BA2121; font-style: italic }} /* Literal.String.Doc */
                .codehilite .s2 {{ color: #BA2121 }} /* Literal.String.Double */
                .codehilite .se {{ color: #BB6622; font-weight: bold }} /* Literal.String.Escape */
                .codehilite .sh {{ color: #BA2121 }} /* Literal.String.Heredoc */
                .codehilite .si {{ color: #BB6688; font-weight: bold }} /* Literal.String.Interpol */
                .codehilite .sx {{ color: #008000 }} /* Literal.String.Other */
                .codehilite .sr {{ color: #BB6688 }} /* Literal.String.Regex */
                .codehilite .s1 {{ color: #BA2121 }} /* Literal.String.Single */
                .codehilite .ss {{ color: #19177C }} /* Literal.String.Symbol */
                .codehilite .bp {{ color: #008000 }} /* Name.Builtin.Pseudo */
                .codehilite .vc {{ color: #19177C }} /* Name.Variable.Class */
                .codehilite .vg {{ color: #19177C }} /* Name.Variable.Global */
                .codehilite .vi {{ color: #19177C }} /* Name.Variable.Instance */
                .codehilite .il {{ color: #666666 }} /* Literal.Number.Integer.Long */
            </style>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        return html


def main():
    app = QApplication(sys.argv)
    viewer = MarkdownViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()