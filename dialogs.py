"""Модуль с диалоговыми окнами"""
import tkinter as tk
from tkinter import messagebox


class AddSecretDialog:
    #Диалог добавления нового секрета

    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.result = None
        self.create_dialog()

    def create_dialog(self):
        #Создание диалогового окна
        dialog = tk.Toplevel(self.parent)
        dialog.title("Добавить новый секрет")
        dialog.geometry("450x350")
        dialog.transient(self.parent)
        dialog.grab_set()

        dialog.configure(bg=self.theme["bg_secondary"])

        fields = [
            ("Название:*", "name", True),
            ("Хост:", "host", False),
            ("Порт:", "port", False),
            ("База данных:", "database", False),
            ("Логин:*", "username", True),
            ("Пароль:*", "password", True)
        ]

        self.entries = {}
        for i, (label, field_name, required) in enumerate(fields):
            tk.Label(dialog, text=label, bg=self.theme["bg_secondary"], fg=self.theme["fg"]).grid(
                row=i, column=0, sticky=tk.W, padx=10, pady=8)

            show_char = "*" if field_name == "password" else None
            entry = tk.Entry(dialog, width=30, bg=self.theme["entry_bg"], fg=self.theme["entry_fg"],
                             insertbackground=self.theme["fg"], relief="flat", show=show_char)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=10, pady=8)
            self.entries[field_name] = entry

        self.entries["name"].focus()

        btn_frame = tk.Frame(dialog, bg=self.theme["bg_secondary"])
        btn_frame.grid(row=6, column=0, columnspan=2, pady=15)

        save_btn = tk.Button(btn_frame, text="Сохранить", bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                             command=lambda: self.save(dialog))
        save_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(btn_frame, text="Отмена", bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                               command=dialog.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)

        dialog.bind('<Return>', lambda e: self.save(dialog))
        dialog.columnconfigure(1, weight=1)
        self.parent.wait_window(dialog)

    def save(self, dialog):
        #Сохранение данных секрета
        name = self.entries["name"].get().strip()
        host = self.entries["host"].get().strip()
        port = self.entries["port"].get().strip()
        database = self.entries["database"].get().strip()
        username = self.entries["username"].get().strip()
        password = self.entries["password"].get()

        if not name:
            messagebox.showerror("Ошибка", "Введите название секрета")
            self.entries["name"].focus()
            return

        if not username:
            messagebox.showerror("Ошибка", "Введите логин")
            self.entries["username"].focus()
            return

        if not password:
            messagebox.showerror("Ошибка", "Введите пароль")
            self.entries["password"].focus()
            return

        secret_data = {
            'host': host, 'port': port, 'database': database,
            'username': username, 'password': password, 'type': 'Database'
        }

        self.result = (name, secret_data)
        dialog.destroy()