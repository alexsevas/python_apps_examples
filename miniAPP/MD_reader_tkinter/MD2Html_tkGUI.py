# conda activate allpy311

# pip install markdown

import tkinter as tk
from tkinter import filedialog
import markdown
from tkinter.scrolledtext import ScrolledText

class MarkdownViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Viewer")
        self.root.geometry("800x600")

        # Создаем меню
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        root.config(menu=menubar)

        # Создаем текстовое поле для отображения Markdown
        self.text_area = ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Markdown Files", "*.md")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                html_content = markdown.markdown(content, extensions=['fenced_code', 'codehilite'])
                self.display_html(html_content)

    def display_html(self, html_content):
        # Очищаем текстовое поле
        self.text_area.config(state='normal')
        self.text_area.delete(1.0, tk.END)

        # Вставляем HTML-содержимое (для простоты отображаем как текст)
        # В реальном приложении можно использовать HTML-рендеринг (например, через tkinter.html)
        self.text_area.insert(tk.END, html_content)
        self.text_area.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownViewer(root)
    root.mainloop()

'''

'''