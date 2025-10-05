import tkinter as tk
from tkinter import messagebox


class PasswordDialog:
    #Базовый диалог для ввода пароля

    def __init__(self, parent, title, prompt, theme=None):
        self.parent = parent
        self.title = title
        self.prompt = prompt
        self.theme = theme or {}
        self.result = None

    def show(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.title)
        dialog.geometry("300x150")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Используем тему или значения по умолчанию
        if self.theme:
            bg_color = self.theme.get("bg_secondary", "black")
            fg_color = self.theme.get("fg", "white")
            entry_bg = self.theme.get("entry_bg", "black")
            entry_fg = self.theme.get("entry_fg", "white")
            cursor_color = self.theme.get("cursor_color", "white")
            button_bg = self.theme.get("button_bg", "#333333")
            button_fg = self.theme.get("button_fg", "white")
        else:
            # Значения по умолчанию для экрана блокировки
            bg_color = "black"
            fg_color = "white"
            entry_bg = "black"
            entry_fg = "white"
            cursor_color = "white"
            button_bg = "#333333"
            button_fg = "white"

        dialog.configure(bg=bg_color)

        # Центрирование на экране
        dialog.update_idletasks()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - dialog.winfo_width()) // 2
        y = (screen_height - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        result = [None]

        tk.Label(dialog, text=self.prompt, bg=bg_color, fg=fg_color, wraplength=280).pack(pady=10)

        password_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=password_var, show='*',
                         bg=entry_bg, fg=entry_fg, insertbackground=cursor_color,
                         width=30, relief="solid", bd=1)
        entry.pack(pady=5)
        entry.focus()

        def on_ok():
            result[0] = password_var.get()
            dialog.destroy()

        def on_cancel():
            result[0] = ""
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg=bg_color)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="OK", command=on_ok,
                  bg=button_bg, fg=button_fg, relief="solid", bd=1).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=on_cancel,
                  bg=button_bg, fg=button_fg, relief="solid", bd=1).pack(side=tk.LEFT, padx=5)

        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())

        self.parent.wait_window(dialog)
        return result[0]


class SecretPasswordDialog(PasswordDialog):
    #Диалог для ввода пароля при работе с секретами

    def __init__(self, parent, secret_name, action, theme):
        prompt = f"Введите мастер-пароль для {action} секрета '{secret_name}':"
        super().__init__(parent, "Мастер-пароль", prompt, theme)


class AddSecretDialog:
    #Диалог добавления нового секрета

    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.result = None
        self.create_dialog()

    def create_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Добавить новый секрет")
        dialog.geometry("450x350")
        dialog.transient(self.parent)
        dialog.grab_set()

        dialog.configure(bg=self.theme["bg_secondary"])

        dialog.update_idletasks()
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - dialog.winfo_width()) // 2
        y = (screen_height - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        fields = [
            ("Название:*", "name", True, False),
            ("Хост:", "host", False, False),
            ("Логин:*", "username", True, False),
            ("Пароль:*", "password", True, True)
        ]

        self.entries = {}
        self.show_password = False
        self.password_buttons = {}

        for i, (label, field_name, required, is_password) in enumerate(fields):
            tk.Label(dialog, text=label, bg=self.theme["bg_secondary"], fg=self.theme["fg"]).grid(
                row=i, column=0, sticky=tk.W, padx=10, pady=8)

            show_char = "*" if is_password and not self.show_password else None
            entry = tk.Entry(dialog, width=25, bg=self.theme["entry_bg"], fg=self.theme["entry_fg"],
                             insertbackground=self.theme["cursor_color"], relief="flat", show=show_char)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=8)
            self.entries[field_name] = entry

            if is_password:
                self.password_buttons[field_name] = tk.Button(
                    dialog, text="👁", width=3, bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                    command=lambda f=field_name: self.toggle_password_visibility(f)
                )
                self.password_buttons[field_name].grid(row=i, column=2, padx=(0, 10), pady=8)

        self.entries["name"].focus()

        btn_frame = tk.Frame(dialog, bg=self.theme["bg_secondary"])
        btn_frame.grid(row=4, column=0, columnspan=3, pady=15)  # Изменил row на 4

        save_btn = tk.Button(btn_frame, text="Сохранить", bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                             command=lambda: self.save(dialog))
        save_btn.grid(row=0, column=0, padx=10)

        cancel_btn = tk.Button(btn_frame, text="Отмена", bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                               command=dialog.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)

        dialog.bind('<Return>', lambda e: self.save(dialog))
        dialog.columnconfigure(1, weight=1)
        self.parent.wait_window(dialog)

    def toggle_password_visibility(self, field_name):
        #Переключение видимости пароля
        entry = self.entries[field_name]
        button = self.password_buttons[field_name]

        if entry.cget('show') == '*':
            entry.config(show='')
            button.config(text="🙈")
        else:
            entry.config(show='*')
            button.config(text="👁")

    def save(self, dialog):
        name = self.entries["name"].get().strip()
        host = self.entries["host"].get().strip()
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
            'host': host,
            'username': username,
            'password': password,
            'type': 'Database'
        }

        self.result = (name, secret_data)
        dialog.destroy()