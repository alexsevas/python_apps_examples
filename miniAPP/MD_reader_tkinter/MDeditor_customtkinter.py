# conda activate allpy311

import customtkinter as ctk
import markdown
from tkinter import filedialog, messagebox
import re


class MarkdownViewerEditor(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.title("Markdown Viewer & Editor")
        self.geometry("1200x700")

        # Установка темы
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Переменные
        self.current_file = None
        self.is_modified = False

        # Создание виджетов
        self.create_widgets()

        # Привязка событий
        self.bind_events()

        # Начальный текст
        self.editor_text.insert("1.0",
                                "# Заголовок 1\n\n## Заголовок 2\n\n### Заголовок 3\n\n**Жирный текст**\n\n*Курсивный текст*\n\n`Код в строке`\n\n```\nБлок кода\nс несколькими строками\n```\n\n- Пункт списка 1\n- Пункт списка 2\n- Пункт списка 3\n\n1. Нумерованный список 1\n2. Нумерованный список 2\n\n[Ссылка на Google](https://google.com)\n\n| Колонка 1 | Колонка 2 |\n|-----------|-----------|\n| Ячейка 1  | Ячейка 2  |")
        self.update_viewer()

    def create_widgets(self):
        # Главный фрейм
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Фрейм для кнопок
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", padx=5, pady=5)

        # Кнопки
        self.open_button = ctk.CTkButton(
            self.button_frame,
            text="Открыть",
            command=self.open_file
        )
        self.open_button.pack(side="left", padx=5)

        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Сохранить",
            command=self.save_file
        )
        self.save_button.pack(side="left", padx=5)

        self.save_as_button = ctk.CTkButton(
            self.button_frame,
            text="Сохранить как",
            command=self.save_file_as
        )
        self.save_as_button.pack(side="left", padx=5)

        # Фрейм для редактора и просмотрщика
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Конфигурация сетки
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Текстовый редактор (левая часть)
        self.editor_frame = ctk.CTkFrame(self.content_frame)
        self.editor_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(1, weight=1)

        self.editor_label = ctk.CTkLabel(
            self.editor_frame,
            text="Редактор",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.editor_label.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.editor_text = ctk.CTkTextbox(
            self.editor_frame,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.editor_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        # Просмотрщик markdown (правая часть)
        self.viewer_frame = ctk.CTkFrame(self.content_frame)
        self.viewer_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.viewer_frame.grid_columnconfigure(0, weight=1)
        self.viewer_frame.grid_rowconfigure(1, weight=1)

        self.viewer_label = ctk.CTkLabel(
            self.viewer_frame,
            text="Просмотр",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.viewer_label.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Создаем текстовый виджет для отображения HTML
        self.html_text = ctk.CTkTextbox(
            self.viewer_frame,
            wrap="word",
            state="normal",
            font=ctk.CTkFont(size=12)
        )
        self.html_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        # Настройка тегов для стилизации
        self.setup_html_tags()

        # Изначально отключаем viewer_text
        self.html_text.configure(state="disabled")

    def setup_html_tags(self):
        """Настройка тегов для HTML-стилизации (без параметра font)"""
        # Заголовки с разным цветом и отступами
        self.html_text.tag_config("h1", foreground="#1a365d", spacing3=15)
        self.html_text.tag_config("h2", foreground="#2c5282", spacing3=12)
        self.html_text.tag_config("h3", foreground="#2b6cb0", spacing3=10)
        self.html_text.tag_config("h4", foreground="#3182ce", spacing3=8)
        self.html_text.tag_config("h5", foreground="#4299e1", spacing3=6)
        self.html_text.tag_config("h6", foreground="#63b3ed", spacing3=4)

        # Стили текста
        self.html_text.tag_config("bold", foreground="#000000")
        self.html_text.tag_config("italic", foreground="#4a5568")
        self.html_text.tag_config("code", background="#f7fafc", foreground="#2d3748")
        self.html_text.tag_config("code_block", background="#f7fafc", foreground="#2d3748", lmargin1=20, lmargin2=20)

        # Ссылки
        self.html_text.tag_config("link", foreground="#3182ce", underline=True)

        # Списки
        self.html_text.tag_config("ul", lmargin1=20, lmargin2=20)
        self.html_text.tag_config("ol", lmargin1=20, lmargin2=20)

        # Таблицы
        self.html_text.tag_config("table", background="#ffffff")

    def bind_events(self):
        """Привязка событий"""
        self.editor_text.bind("<KeyRelease>", self.on_text_change)
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-n>", lambda e: self.new_file())

    def on_text_change(self, event=None):
        """Обработчик изменения текста"""
        self.is_modified = True
        self.update_viewer()

    def update_viewer(self):
        """Обновление просмотра markdown"""
        # Получаем текст из редактора
        markdown_text = self.editor_text.get("1.0", "end-1c")

        # Конвертируем markdown в HTML с расширениями
        html = markdown.markdown(
            markdown_text,
            extensions=[
                'fenced_code',
                'tables',
                'toc',
                'nl2br'
            ]
        )

        # Очищаем просмотрщик
        self.html_text.configure(state="normal")
        self.html_text.delete("1.0", "end")

        # Вставляем HTML и применяем стилизацию
        self.insert_html_content(html)

        self.html_text.configure(state="disabled")

    def insert_html_content(self, html):
        """Вставка HTML контента с применением стилей"""
        # Парсинг HTML и применение стилей
        self.parse_and_insert_html(html)

    def parse_and_insert_html(self, html):
        """Парсинг HTML и вставка с применением тегов"""
        # Простой парсер HTML для базовой стилизации
        import re

        # Заголовки
        def replace_h1(match):
            return f"[H1]{match.group(1)}[/H1]\n"

        html = re.sub(r'<h1>(.*?)</h1>', replace_h1, html, flags=re.DOTALL)

        def replace_h2(match):
            return f"[H2]{match.group(1)}[/H2]\n"

        html = re.sub(r'<h2>(.*?)</h2>', replace_h2, html, flags=re.DOTALL)

        def replace_h3(match):
            return f"[H3]{match.group(1)}[/H3]\n"

        html = re.sub(r'<h3>(.*?)</h3>', replace_h3, html, flags=re.DOTALL)

        def replace_h4(match):
            return f"[H4]{match.group(1)}[/H4]\n"

        html = re.sub(r'<h4>(.*?)</h4>', replace_h4, html, flags=re.DOTALL)

        def replace_h5(match):
            return f"[H5]{match.group(1)}[/H5]\n"

        html = re.sub(r'<h5>(.*?)</h5>', replace_h5, html, flags=re.DOTALL)

        def replace_h6(match):
            return f"[H6]{match.group(1)}[/H6]\n"

        html = re.sub(r'<h6>(.*?)</h6>', replace_h6, html, flags=re.DOTALL)

        # Жирный текст
        html = re.sub(r'<strong>(.*?)</strong>', r'[BOLD]\1[/BOLD]', html)
        html = re.sub(r'<b>(.*?)</b>', r'[BOLD]\1[/BOLD]', html)

        # Курсив
        html = re.sub(r'<em>(.*?)</em>', r'[ITALIC]\1[/ITALIC]', html)
        html = re.sub(r'<i>(.*?)</i>', r'[ITALIC]\1[/ITALIC]', html)

        # Код
        html = re.sub(r'<code>(.*?)</code>', r'[CODE]\1[/CODE]', html)

        # Блоки кода
        def replace_code_block(match):
            content = match.group(1)
            # Удаляем лишние отступы
            content = content.strip()
            return f"\n[CODE_BLOCK]{content}[/CODE_BLOCK]\n"

        html = re.sub(r'<pre><code>(.*?)</code></pre>', replace_code_block, html, flags=re.DOTALL)

        # Ссылки
        def replace_link(match):
            url, text = match.groups()
            return f'[LINK:{url}]{text}[/LINK]'

        html = re.sub(r'<a href="(.*?)">(.*?)</a>', replace_link, html)

        # Списки
        html = re.sub(r'<li>(.*?)</li>', r'• \1\n', html)
        html = re.sub(r'<ul>(.*?)</ul>', r'[UL]\1[/UL]\n', html, flags=re.DOTALL)
        html = re.sub(r'<ol>(.*?)</ol>', r'[OL]\1[/OL]\n', html, flags=re.DOTALL)

        # Абзацы
        html = re.sub(r'<p>(.*?)</p>', r'\1\n\n', html)

        # Таблицы (упрощенная обработка)
        html = re.sub(r'<table>(.*?)</table>', r'[TABLE]\1[/TABLE]\n', html, flags=re.DOTALL)
        html = re.sub(r'<tr>(.*?)</tr>', r'\1\n', html, flags=re.DOTALL)
        html = re.sub(r'<td>(.*?)</td>', r'|\1', html, flags=re.DOTALL)
        html = re.sub(r'<th>(.*?)</th>', r'|\1', html, flags=re.DOTALL)

        # Удаление остальных тегов
        html = re.sub(r'<[^>]+>', '', html)

        # Вставка текста
        self.html_text.insert("1.0", html)

        # Применение тегов
        self.apply_html_tags()

    def apply_html_tags(self):
        """Применение тегов к HTML контенту"""
        content = self.html_text.get("1.0", "end-1c")
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Обработка заголовков
            if '[H1]' in line and '[/H1]' in line:
                start = line.find('[H1]') + 4
                end = line.find('[/H1]')
                self.html_text.delete(f"{i}.{start - 4}", f"{i}.{start}")
                self.html_text.delete(f"{i}.{end - 4}", f"{i}.{end}")
                self.html_text.tag_add("h1", f"{i}.0", f"{i}.end")

            elif '[H2]' in line and '[/H2]' in line:
                start = line.find('[H2]') + 4
                end = line.find('[/H2]')
                self.html_text.delete(f"{i}.{start - 4}", f"{i}.{start}")
                self.html_text.delete(f"{i}.{end - 4}", f"{i}.{end}")
                self.html_text.tag_add("h2", f"{i}.0", f"{i}.end")

            elif '[H3]' in line and '[/H3]' in line:
                start = line.find('[H3]') + 4
                end = line.find('[/H3]')
                self.html_text.delete(f"{i}.{start - 4}", f"{i}.{start}")
                self.html_text.delete(f"{i}.{end - 4}", f"{i}.{end}")
                self.html_text.tag_add("h3", f"{i}.0", f"{i}.end")

            elif '[H4]' in line and '[/H4]' in line:
                start = line.find('[H4]') + 4
                end = line.find('[/H4]')
                self.html_text.delete(f"{i}.{start - 4}", f"{i}.{start}")
                self.html_text.delete(f"{i}.{end - 4}", f"{i}.{end}")
                self.html_text.tag_add("h4", f"{i}.0", f"{i}.end")

            elif '[H5]' in line and '[/H5]' in line:
                start = line.find('[H5]') + 4
                end = line.find('[/H5]')
                self.html_text.delete(f"{i}.{start - 4}", f"{i}.{start}")
                self.html_text.delete(f"{i}.{end - 4}", f"{i}.{end}")
                self.html_text.tag_add("h5", f"{i}.0", f"{i}.end")

            elif '[H6]' in line and '[/H6]' in line:
                start = line.find('[H6]') + 4
                end = line.find('[/H6]')
                self.html_text.delete(f"{i}.{start - 4}", f"{i}.{start}")
                self.html_text.delete(f"{i}.{end - 4}", f"{i}.{end}")
                self.html_text.tag_add("h6", f"{i}.0", f"{i}.end")

            # Обработка жирного текста
            start_pos = 0
            while True:
                bold_start = line.find('[BOLD]', start_pos)
                if bold_start == -1:
                    break
                bold_end = line.find('[/BOLD]', bold_start)
                if bold_end == -1:
                    break

                # Удаляем маркеры
                self.html_text.delete(f"{i}.{bold_start}", f"{i}.{bold_start + 6}")
                self.html_text.delete(f"{i}.{bold_end - 6}", f"{i}.{bold_end}")

                # Применяем тег
                self.html_text.tag_add("bold", f"{i}.{bold_start}", f"{i}.{bold_end - 6}")

                start_pos = bold_end - 6

            # Обработка курсива
            start_pos = 0
            while True:
                italic_start = line.find('[ITALIC]', start_pos)
                if italic_start == -1:
                    break
                italic_end = line.find('[/ITALIC]', italic_start)
                if italic_end == -1:
                    break

                # Удаляем маркеры
                self.html_text.delete(f"{i}.{italic_start}", f"{i}.{italic_start + 8}")
                self.html_text.delete(f"{i}.{italic_end - 8}", f"{i}.{italic_end}")

                # Применяем тег
                self.html_text.tag_add("italic", f"{i}.{italic_start}", f"{i}.{italic_end - 8}")

                start_pos = italic_end - 8

            # Обработка кода
            start_pos = 0
            while True:
                code_start = line.find('[CODE]', start_pos)
                if code_start == -1:
                    break
                code_end = line.find('[/CODE]', code_start)
                if code_end == -1:
                    break

                # Удаляем маркеры
                self.html_text.delete(f"{i}.{code_start}", f"{i}.{code_start + 6}")
                self.html_text.delete(f"{i}.{code_end - 6}", f"{i}.{code_end}")

                # Применяем тег
                self.html_text.tag_add("code", f"{i}.{code_start}", f"{i}.{code_end - 6}")

                start_pos = code_end - 6

            # Обработка блоков кода
            start_pos = 0
            while True:
                code_block_start = line.find('[CODE_BLOCK]', start_pos)
                if code_block_start == -1:
                    break
                code_block_end = line.find('[/CODE_BLOCK]', code_block_start)
                if code_block_end == -1:
                    break

                # Удаляем маркеры
                self.html_text.delete(f"{i}.{code_block_start}", f"{i}.{code_block_start + 12}")
                self.html_text.delete(f"{i}.{code_block_end - 12}", f"{i}.{code_block_end}")

                # Применяем тег
                self.html_text.tag_add("code_block", f"{i}.{code_block_start}", f"{i}.{code_block_end - 12}")

                start_pos = code_block_end - 12

            # Обработка ссылок
            start_pos = 0
            while True:
                link_start = line.find('[LINK:', start_pos)
                if link_start == -1:
                    break
                link_middle = line.find(']', link_start)
                if link_middle == -1:
                    break
                link_end = line.find('[/LINK]', link_middle)
                if link_end == -1:
                    break

                # Удаляем маркеры
                self.html_text.delete(f"{i}.{link_start}", f"{i}.{link_middle + 1}")
                self.html_text.delete(f"{i}.{link_end - 7}", f"{i}.{link_end}")

                # Применяем тег
                self.html_text.tag_add("link", f"{i}.{link_start}", f"{i}.{link_end - 7}")

                start_pos = link_end - 7

    def new_file(self):
        """Создание нового файла"""
        if self.check_unsaved_changes():
            self.editor_text.delete("1.0", "end")
            self.current_file = None
            self.is_modified = False
            self.update_viewer()

    def open_file(self):
        """Открытие файла"""
        if self.check_unsaved_changes():
            file_path = filedialog.askopenfilename(
                title="Открыть markdown файл",
                filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
            )

            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.editor_text.delete("1.0", "end")
                        self.editor_text.insert("1.0", content)
                        self.current_file = file_path
                        self.is_modified = False
                        self.update_viewer()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")

    def save_file(self):
        """Сохранение файла"""
        if self.current_file:
            try:
                content = self.editor_text.get("1.0", "end-1c")
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.is_modified = False
                messagebox.showinfo("Сохранение", "Файл успешно сохранен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Сохранение файла с новым именем"""
        file_path = filedialog.asksaveasfilename(
            title="Сохранить markdown файл",
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )

        if file_path:
            try:
                content = self.editor_text.get("1.0", "end-1c")
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.current_file = file_path
                self.is_modified = False
                messagebox.showinfo("Сохранение", "Файл успешно сохранен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def check_unsaved_changes(self):
        """Проверка несохраненных изменений"""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Несохраненные изменения",
                "У вас есть несохраненные изменения. Хотите сохранить их?"
            )
            if result is True:
                self.save_file()
                return not self.is_modified  # Возвращаем True, если сохранение прошло успешно
            elif result is False:
                return True  # Продолжаем без сохранения
            else:
                return False  # Отмена операции
        return True


if __name__ == "__main__":
    app = MarkdownViewerEditor()
    app.mainloop()