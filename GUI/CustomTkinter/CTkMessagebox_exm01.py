# conda activate allpy311

'''
Библиотека CTkMessagebox — это дополнение к библиотеке CustomTkinter, которая предоставляет современные настраиваемые
элементы интерфейса для Python.
CTkMessagebox позволяет создавать диалоговые окна с сообщениями, кнопками и различными вариантами действий в стиле CustomTkinter.
'''

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

# Инициализация CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Создание главного окна
root = ctk.CTk()
root.geometry("400x300")
root.title("Пример CTkMessagebox")


def show_messagebox():
    msg_box = CTkMessagebox(
        title="Пример сообщения",
        message="Вы уверены, что хотите продолжить?",
        icon="question",  # Доступные иконки: 'info', 'warning', 'error', 'question'
        option_1="Да",
        option_2="Нет"
    )
    result = msg_box.get()  # Получение результата нажатия кнопки
    print(f"Нажата кнопка: {result}")


# Кнопка для вызова CTkMessagebox
button = ctk.CTkButton(root, text="Показать сообщение", command=show_messagebox)
button.pack(pady=20)

root.mainloop()
