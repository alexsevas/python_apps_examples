# conda activate allpy311

import tkinter as tk
from tkinter import filedialog, messagebox
import markdown
from tkinter.scrolledtext import ScrolledText
import os

class MarkdownEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Editor & Viewer")
        self.root.geometry("1200x700")

        self.current_file = None
        self.unsaved_changes = False

        # Создаем меню
        self.create_menu()

        # Создаем основной фрейм
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаем фреймы для редактора и предпросмотра
        editor_frame = tk.Frame(main_frame, relief=tk.SUNKEN, bd=1)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))

        preview_frame = tk.Frame(main_frame, relief=tk.SUNKEN, bd=1)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2, 0))

        # Заголовки панелей
        editor_label = tk.Label(editor_frame, text="Редактор", font=("Arial", 10, "bold"))
        editor_label.pack(pady=2)

        preview_label = tk.Label(preview_frame, text="Предпросмотр", font=("Arial", 10, "bold"))
        preview_label.pack(pady=2)

        # Создаем текстовый редактор
        self.editor = ScrolledText(editor_frame, wrap=tk.WORD, font=("Consolas", 11))
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.bind('<KeyRelease>', self.on_text_change)

        # Создаем текстовое поле для предпросмотра
        self.preview = ScrolledText(preview_frame, wrap=tk.WORD, state='disabled', font=("Arial", 11))
        self.preview.pack(fill=tk.BOTH, expand=True)

        # Статусная строка
        self.status_bar = tk.Label(root, text="Готов", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Инициализация
        self.update_preview()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Новый", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.exit_app)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Отменить", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить всё", command=self.select_all, accelerator="Ctrl+A")
        menubar.add_cascade(label="Правка", menu=edit_menu)

        # Меню Помощь
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Помощь", menu=help_menu)

        # Привязки клавиш
        self.root.bind('<Control-n>', lambda event: self.new_file())
        self.root.bind('<Control-o>', lambda event: self.open_file())
        self.root.bind('<Control-s>', lambda event: self.save_file())
        self.root.bind('<Control-S>', lambda event: self.save_as_file())
        self.root.bind('<Control-z>', lambda event: self.undo())
        self.root.bind('<Control-y>', lambda event: self.redo())
        self.root.bind('<Control-x>', lambda event: self.cut())
        self.root.bind('<Control-c>', lambda event: self.copy())
        self.root.bind('<Control-v>', lambda event: self.paste())
        self.root.bind('<Control-a>', lambda event: self.select_all())

    def on_text_change(self, event=None):
        self.unsaved_changes = True
        self.update_status()
        self.update_preview()

    def update_preview(self):
        content = self.editor.get(1.0, tk.END)
        try:
            # Преобразуем Markdown в HTML с расширениями
            html_content = markdown.markdown(
                content,
                extensions=[
                    'fenced_code',
                    'codehilite',
                    'tables',
                    'toc',
                    'nl2br',
                    'sane_lists'
                ]
            )
            self.display_html(html_content)
        except Exception as e:
            # В случае ошибки показываем простой текст
            self.display_html(content)

    def display_html(self, html_content):
        self.preview.config(state='normal')
        self.preview.delete(1.0, tk.END)

        # Здесь можно добавить более сложную обработку HTML
        # Пока просто отображаем как текст
        self.preview.insert(tk.END, html_content)
        self.preview.config(state='disabled')

    def update_status(self):
        filename = os.path.basename(self.current_file) if self.current_file else "Новый файл"
        status = f"{filename} - {'*' if self.unsaved_changes else ''}"
        self.status_bar.config(text=status)

    def new_file(self):
        if self.unsaved_changes:
            if not self.ask_save_changes():
                return
        self.editor.delete(1.0, tk.END)
        self.current_file = None
        self.unsaved_changes = False
        self.update_status()

    def open_file(self):
        if self.unsaved_changes:
            if not self.ask_save_changes():
                return

        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Markdown Files", "*.md"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    self.editor.delete(1.0, tk.END)
                    self.editor.insert(1.0, content)
                    self.current_file = file_path
                    self.unsaved_changes = False
                    self.update_status()
                    self.update_preview()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")

    def save_file(self):
        if self.current_file:
            try:
                content = self.editor.get(1.0, tk.END)
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(content)
                self.unsaved_changes = False
                self.update_status()
                messagebox.showinfo("Сохранение", "Файл успешно сохранен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[
                ("Markdown Files", "*.md"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            try:
                content = self.editor.get(1.0, tk.END)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self.current_file = file_path
                self.unsaved_changes = False
                self.update_status()
                messagebox.showinfo("Сохранение", "Файл успешно сохранен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def ask_save_changes(self):
        result = messagebox.askyesnocancel(
            "Несохраненные изменения",
            "У вас есть несохраненные изменения. Хотите сохранить их?"
        )
        if result is True:  # Да
            self.save_file()
            return True
        elif result is False:  # Нет
            return True
        else:  # Отмена
            return False

    def exit_app(self):
        if self.unsaved_changes:
            if not self.ask_save_changes():
                return
        self.root.quit()

    def undo(self):
        try:
            self.editor.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.editor.edit_redo()
        except tk.TclError:
            pass

    def cut(self):
        try:
            self.editor.event_generate("<<Cut>>")
        except tk.TclError:
            pass

    def copy(self):
        try:
            self.editor.event_generate("<<Copy>>")
        except tk.TclError:
            pass

    def paste(self):
        try:
            self.editor.event_generate("<<Paste>>")
        except tk.TclError:
            pass

    def select_all(self):
        self.editor.tag_add(tk.SEL, "1.0", tk.END)
        self.editor.mark_set(tk.INSERT, "1.0")
        self.editor.see(tk.INSERT)
        return "break"

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Markdown Editor & Viewer\n\n"
            "Простой редактор Markdown с возможностью предпросмотра\n"
            "в реальном времени."
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownEditor(root)
    root.mainloop()