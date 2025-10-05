import tkinter as tk
from tkinter import messagebox


class PasswordDialog:
    def __init__(self, parent, title, prompt, theme=None):
        self.parent = parent
        self.title = title
        self.prompt = prompt
        self.theme = theme or {}
        self.result = None

    def show(self):
        # Используем серый фон вместо черного
        dialog_frame = tk.Frame(self.parent, bg="#2f3136", relief="flat", bd=0)
        dialog_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER, width=450, height=250)

        if self.theme:
            bg_color = self.theme.get("bg_secondary", "#2f3136")  # Серый фон по умолчанию
            fg_color = self.theme.get("fg", "white")
            entry_bg = self.theme.get("entry_bg", "#40444b")
            entry_fg = self.theme.get("entry_fg", "white")
            cursor_color = self.theme.get("cursor_color", "white")
        else:
            bg_color = "#2f3136"  # Серый фон
            fg_color = "white"
            entry_bg = "#40444b"  # Серый для поля ввода
            entry_fg = "white"
            cursor_color = "white"

        dialog_frame.configure(bg=bg_color)
        result = [None]

        title_label = tk.Label(dialog_frame, text=self.title, bg=bg_color, fg=fg_color,
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(20, 8))

        prompt_label = tk.Label(dialog_frame, text=self.prompt, bg=bg_color, fg=fg_color,
                                wraplength=400, justify=tk.CENTER, font=("Arial", 12))
        prompt_label.pack(pady=8)

        password_frame = tk.Frame(dialog_frame, bg=bg_color)
        password_frame.pack(pady=12)

        password_var = tk.StringVar()
        self.entry = tk.Entry(password_frame, textvariable=password_var, show='*',
                              bg=entry_bg, fg=entry_fg, insertbackground=cursor_color,
                              width=28, relief="solid", bd=1, font=("Arial", 12))
        self.entry.pack(side=tk.LEFT, padx=(0, 8))
        self.entry.focus()

        self.show_password_btn = tk.Button(password_frame, text="👁", width=4,
                                           bg="#333333", fg="white", relief="solid", bd=1,
                                           command=self.toggle_password_visibility,
                                           font=("Arial", 10))
        self.show_password_btn.pack(side=tk.LEFT)
        self.password_visible = False

        btn_frame = tk.Frame(dialog_frame, bg=bg_color)
        btn_frame.pack(pady=15)

        def on_ok():
            result[0] = password_var.get()
            dialog_frame.destroy()

        def on_cancel():
            result[0] = ""
            dialog_frame.destroy()

        ok_btn = tk.Button(btn_frame, text="OK", command=on_ok,
                           bg="#007bff", fg="white", relief="solid", bd=1,
                           width=10, font=("Arial", 11, "bold"),
                           activebackground="#e6f2ff", activeforeground="#007bff")
        ok_btn.pack(side=tk.LEFT, padx=12)

        ok_btn.bind("<Enter>", lambda e: ok_btn.config(bg="#e6f2ff", fg="#007bff"))
        ok_btn.bind("<Leave>", lambda e: ok_btn.config(bg="#007bff", fg="white"))

        cancel_btn = tk.Button(btn_frame, text="Отмена", command=on_cancel,
                               bg="#dc3545", fg="white", relief="solid", bd=1,
                               width=10, font=("Arial", 11),
                               activebackground="#800000", activeforeground="white")
        cancel_btn.pack(side=tk.LEFT, padx=12)

        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg="#800000"))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg="#dc3545"))

        self.entry.bind('<Return>', lambda e: on_ok())
        self.entry.bind('<Escape>', lambda e: on_cancel())

        self.parent.wait_window(dialog_frame)
        return result[0]

    def toggle_password_visibility(self):
        if self.password_visible:
            self.entry.config(show='*')
            self.show_password_btn.config(text="👁")
            self.password_visible = False
        else:
            self.entry.config(show='')
            self.show_password_btn.config(text="🙈")
            self.password_visible = True


class SecretPasswordDialog(PasswordDialog):
    def __init__(self, parent, secret_name, action, theme):
        prompt = f"Введите мастер-пароль для {action} секрета '{secret_name}':"
        super().__init__(parent, "Мастер-пароль", prompt, theme)


class AddSecretDialog:
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.result = None
        self.create_dialog()

    def create_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Добавить новый секрет")
        dialog.geometry("500x350")
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

        for i, (label, field_name, required, is_password) in enumerate(fields):
            tk.Label(dialog, text=label, bg=self.theme["bg_secondary"], fg=self.theme["fg"],
                     font=("Arial", 11)).grid(
                row=i, column=0, sticky=tk.W, padx=12, pady=10)

            show_char = "*" if is_password else None
            entry = tk.Entry(dialog, width=32, bg=self.theme["entry_bg"], fg=self.theme["entry_fg"],
                             insertbackground=self.theme["cursor_color"], relief="flat",
                             show=show_char, font=("Arial", 11))
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=12, pady=10)
            self.entries[field_name] = entry

        self.entries["name"].focus()

        btn_frame = tk.Frame(dialog, bg=self.theme["bg_secondary"])
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        # Увеличиваем ширину кнопок и уменьшаем шрифт для лучшего размещения текста
        save_btn = tk.Button(btn_frame, text="Сохранить", bg="#007bff", fg="white",
                             command=lambda: self.save(dialog),
                             font=("Arial", 10), width=12, height=1)  # Уменьшен шрифт и задана ширина
        save_btn.grid(row=0, column=0, padx=8, ipadx=5, ipady=2)  # Добавлены внутренние отступы

        cancel_btn = tk.Button(btn_frame, text="Отмена", bg="#dc3545", fg="white",
                               command=dialog.destroy,
                               font=("Arial", 10), width=12, height=1)  # Уменьшен шрифт и задана ширина
        cancel_btn.grid(row=0, column=1, padx=8, ipadx=5, ipady=2)  # Добавлены внутренние отступы

        dialog.bind('<Return>', lambda e: self.save(dialog))
        dialog.columnconfigure(1, weight=1)
        self.parent.wait_window(dialog)

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
