import sqlite3
import json
from datetime import datetime
import base64
import os
import hashlib
import tkinter as tk
from tkinter import messagebox



class Database:
    def __init__(self, db_path='secrets.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                encrypted_data BLOB NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS master_password (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                password_hash TEXT NOT NULL,
                salt BLOB NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def is_master_password_set(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM master_password WHERE id = 1')
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def set_master_password(self, master_password: str) -> bool:
        try:
            if self.is_master_password_set():
                return False
            password_hash, salt = self._hash_password(master_password)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO master_password (id, password_hash, salt)
                VALUES (1, ?, ?)
            ''', (password_hash, salt))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при установке мастер-пароля: {e}")
            return False

    def verify_master_password(self, master_password: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT password_hash, salt FROM master_password WHERE id = 1')
            result = cursor.fetchone()
            conn.close()
            if result:
                stored_hash, salt = result
                return self._verify_password(master_password, stored_hash, salt)
            return False
        except Exception as e:
            print(f"Ошибка при проверке мастер-пароля: {e}")
            return False

    def save_secret(self, name, secret_data, master_password):
        try:
            if not self.verify_master_password(master_password):
                return False
            json_data = json.dumps(secret_data)
            encrypted_data = self._encrypt_data(json_data, master_password)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO secrets (name, encrypted_data, updated_at)
                VALUES (?, ?, ?)
            ''', (name, encrypted_data, datetime.now()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
            return False

    def get_secret(self, name, master_password):
        try:
            if not self.verify_master_password(master_password):
                return None
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT encrypted_data FROM secrets WHERE name = ?', (name,))
            result = cursor.fetchone()
            conn.close()
            if result:
                encrypted_data = result[0]
                decrypted_json = self._decrypt_data(encrypted_data, master_password)
                return json.loads(decrypted_json)
            return None
        except Exception as e:
            print(f"Ошибка при расшифровке: {e}")
            return None

    def search_secrets(self, search_term=''):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if search_term:
            cursor.execute('SELECT name FROM secrets WHERE name LIKE ? ORDER BY name',
                           (f'%{search_term}%',))
        else:
            cursor.execute('SELECT name FROM secrets ORDER BY name')
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results

    def delete_secret(self, name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM secrets WHERE name = ?', (name,))
        conn.commit()
        conn.close()

    def _derive_key(self, master_password: str, salt: bytes = None) -> tuple:
        if salt is None:
            salt = os.urandom(16)
        key = base64.urlsafe_b64encode(hashlib.pbkdf2_hmac(
            'sha256',
            master_password.encode(),
            salt,
            100000,
            32
        ))
        return key, salt

    def _encrypt_data(self, data: str, master_password: str) -> bytes:
        salt = os.urandom(16)
        key, salt = self._derive_key(master_password, salt)
        data_bytes = data.encode()
        encrypted = bytearray()
        key_bytes = base64.urlsafe_b64decode(key)
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        return salt + bytes(encrypted)

    def _decrypt_data(self, encrypted_data: bytes, master_password: str) -> str:
        try:
            salt = encrypted_data[:16]
            actual_data = encrypted_data[16:]
            key, _ = self._derive_key(master_password, salt)
            decrypted = bytearray()
            key_bytes = base64.urlsafe_b64decode(key)
            for i, byte in enumerate(actual_data):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            return decrypted.decode()
        except Exception:
            raise ValueError("Неверный мастер-пароль или поврежденные данные")

    def _hash_password(self, password: str, salt: bytes = None) -> tuple:
        if salt is None:
            salt = os.urandom(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        return base64.b64encode(password_hash).decode(), salt

    def _verify_password(self, password: str, stored_hash: str, salt: bytes) -> bool:
        try:
            new_hash, _ = self._hash_password(password, salt)
            return new_hash == stored_hash
        except:
            return False


class PasswordDialog:
    def __init__(self, parent, title, prompt, theme=None):
        self.parent = parent
        self.title = title
        self.prompt = prompt
        self.theme = theme or {}
        self.result = None

    def show(self):
        dialog_frame = tk.Frame(self.parent, bg="black", relief="raised", bd=2)
        dialog_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER, width=450, height=250)

        if self.theme:
            bg_color = self.theme.get("bg_secondary", "black")
            fg_color = self.theme.get("fg", "white")
            entry_bg = self.theme.get("entry_bg", "black")
            entry_fg = self.theme.get("entry_fg", "white")
            cursor_color = self.theme.get("cursor_color", "white")
        else:
            bg_color = "black"
            fg_color = "white"
            entry_bg = "black"
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

        save_btn = tk.Button(btn_frame, text="Сохранить", bg="#007bff", fg="white",
                             command=lambda: self.save(dialog),
                             font=("Arial", 11, "bold"))
        save_btn.grid(row=0, column=0, padx=12)

        cancel_btn = tk.Button(btn_frame, text="Отмена", bg="#dc3545", fg="white",
                               command=dialog.destroy,
                               font=("Arial", 11))
        cancel_btn.grid(row=0, column=1, padx=12)

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


class LockScreen:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_lock()
        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.draw_lock()

    def draw_lock(self):
        self.canvas.delete("all")
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        if width <= 1 or height <= 1:
            width = 800
            height = 600

        center_x = width // 2
        center_y = height // 2
        size = min(width, height) // 3

        lock_width = size
        lock_height = size * 0.6
        lock_x = center_x - lock_width // 2
        lock_y = center_y - lock_height // 2

        self.create_round_rect(
            lock_x, lock_y,
            lock_x + lock_width, lock_y + lock_height,
            radius=20,
            outline="#ffffff", width=4, fill="#1a1a1a"
        )

        shackle_width = lock_width * 0.5
        shackle_height = lock_height * 0.9
        shackle_x = center_x - shackle_width // 2
        shackle_y = lock_y - shackle_height * 0.6

        self.canvas.create_arc(
            shackle_x, shackle_y,
            shackle_x + shackle_width, shackle_y + shackle_height,
            start=0, extent=180, outline="#ffffff", width=5, style=tk.ARC
        )

        inner_shackle_width = shackle_width * 0.7
        inner_shackle_height = shackle_height * 0.7
        inner_shackle_x = center_x - inner_shackle_width // 2
        inner_shackle_y = shackle_y + (shackle_height - inner_shackle_height) * 0.5

        self.canvas.create_arc(
            inner_shackle_x, inner_shackle_y,
            inner_shackle_x + inner_shackle_width, inner_shackle_y + inner_shackle_height,
            start=0, extent=180, outline="#cccccc", width=2, style=tk.ARC
        )

        keyhole_size = size * 0.12
        self.canvas.create_oval(
            center_x - keyhole_size, center_y - keyhole_size * 0.6,
            center_x + keyhole_size, center_y + keyhole_size * 0.6,
            outline="#ffffff", width=2, fill="#2a2a2a"
        )
        self.canvas.create_oval(
            center_x - keyhole_size * 0.6, center_y - keyhole_size * 0.4,
            center_x + keyhole_size * 0.6, center_y + keyhole_size * 0.4,
            outline="#cccccc", width=1, fill="#1a1a1a"
        )
        self.canvas.create_rectangle(
            center_x - keyhole_size * 0.15, center_y + keyhole_size * 0.3,
            center_x + keyhole_size * 0.15, center_y + keyhole_size * 1.2,
            outline="", fill="#ffffff"
        )

        shine_size = size * 0.08
        self.canvas.create_oval(
            lock_x + lock_width * 0.15, lock_y + lock_height * 0.2,
            lock_x + lock_width * 0.15 + shine_size, lock_y + lock_height * 0.2 + shine_size,
            fill="#ffffff", outline=""
        )

        self.canvas.create_oval(
            center_x - lock_width * 0.4, lock_y + lock_height + 5,
            center_x + lock_width * 0.4, lock_y + lock_height + 15,
            fill="#333333", outline=""
        )

        self.canvas.create_text(
            center_x, lock_y + lock_height + 50,
            text="Введите мастер-пароль для доступа",
            fill="#ffffff", font=("Arial", 16, "bold")
        )

    def create_round_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = []
        points.extend([x1 + radius, y1])
        points.extend([x2 - radius, y1])
        points.extend([x2, y1])
        points.extend([x2, y1 + radius])
        points.extend([x2, y2 - radius])
        points.extend([x2, y2])
        points.extend([x2 - radius, y2])
        points.extend([x1 + radius, y2])
        points.extend([x1, y2])
        points.extend([x1, y2 - radius])
        points.extend([x1, y1 + radius])
        points.extend([x1, y1])

        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def destroy(self):
        self.canvas.destroy()


class Theme:
    def __init__(self):
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                "bg": "#2f3136", "bg_secondary": "#36393f", "bg_tertiary": "#40444b",
                "fg": "#ffffff", "fg_secondary": "#b9bbbe", "accent": "#007bff",
                "accent_hover": "#0056b3", "entry_bg": "#40444b", "entry_fg": "#ffffff",
                "listbox_bg": "#40444b", "listbox_fg": "#ffffff", "text_bg": "#40444b",
                "text_fg": "#ffffff", "button_bg": "#007bff", "button_fg": "#ffffff",
                "status_bg": "#36393f", "status_fg": "#b9bbbe", "scrollbar_bg": "#007bff",
                "scrollbar_trough": "#40444b", "scrollbar_active": "#0056b3",
                "cursor_color": "#ffffff"
            },
            "light": {
                "bg": "#f8f9fa", "bg_secondary": "#ffffff", "bg_tertiary": "#e9ecef",
                "fg": "#212529", "fg_secondary": "#6c757d", "accent": "#007bff",
                "accent_hover": "#0056b3", "entry_bg": "#ffffff", "entry_fg": "#212529",
                "listbox_bg": "#ffffff", "listbox_fg": "#212529", "text_bg": "#ffffff",
                "text_fg": "#212529", "button_bg": "#007bff", "button_fg": "#ffffff",
                "status_bg": "#e9ecef", "status_fg": "#6c757d", "scrollbar_bg": "#007bff",
                "scrollbar_trough": "#e9ecef", "scrollbar_active": "#0056b3",
                "cursor_color": "#212529"
            }
        }

    def get_theme(self):
        return self.themes[self.current_theme]

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        return self.get_theme()


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=30, corner_radius=20,
                 bg_color="#007bff", fg_color="#ffffff", hover_color="#0056b3",
                 parent_bg_color="#2f3136", **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        self.command = command
        self.corner_radius = corner_radius
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.parent_bg_color = parent_bg_color
        self.current_color = bg_color
        self.text = text
        self.width = width
        self.height = height

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.draw_button()

    def draw_button(self):
        self.delete("all")
        self.configure(bg=self.parent_bg_color)
        self.create_rounded_rect(0, 0, self.width, self.height, self.corner_radius,
                                 fill=self.current_color, outline="")
        self.create_text(self.width // 2, self.height // 2, text=self.text,
                         fill=self.fg_color, font=("Arial", 11))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1,
            x2, y1 + radius, x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2, x1, y2,
            x1, y2 - radius, x1, y1 + radius, x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.current_color = self.hover_color
        self.draw_button()

    def _on_leave(self, event):
        self.current_color = self.bg_color
        self.draw_button()


class SecretWallet:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Storage of Secrets")

        try:
            self.root.iconphoto(True, tk.PhotoImage(file="Hakaton_image.png"))
        except:
            try:
                self.root.iconphoto(True, tk.PhotoImage(file="Hakaton_image.jpg"))
            except:
                print("Не удалось загрузить иконку приложения")

        self.root.state('zoomed')
        self.db = Database()
        self.current_secret_name = None
        self.current_secret_data = None
        self.theme_manager = Theme()
        self.current_theme = self.theme_manager.get_theme()
        self.lock_screen = LockScreen(root)
        self.verify_master_password_on_startup()

    def verify_master_password_on_startup(self):
        if not self.db.is_master_password_set():
            self.lock_screen.destroy()
            messagebox.showinfo("Настройка", "Установите мастер-пароль для защиты ваших секретов.")

            while True:
                password = self.ask_password("Установка мастер-пароля", "Введите новый мастер-пароль:")
                if not password:
                    if messagebox.askyesno("Подтверждение",
                                           "Без мастер-пароля вы не сможете сохранять секреты. Вы уверены?"):
                        self.root.destroy()
                        return
                    continue

                confirm = self.ask_password("Подтверждение", "Повторите мастер-пароль:")

                if password == confirm:
                    if self.db.set_master_password(password):
                        messagebox.showinfo("Успех", "Мастер-пароль успешно установлен!")
                        self.setup_ui()
                        self.apply_theme()
                        self.load_secrets()
                        break
                    else:
                        messagebox.showerror("Ошибка", "Не удалось установить мастер-пароль")
                else:
                    messagebox.showerror("Ошибка", "Пароли не совпадают. Попробуйте снова.")
        else:
            password = self.ask_password("Мастер-пароль", "Введите мастер-пароль:")
            if not password or not self.db.verify_master_password(password):
                messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
                self.root.destroy()
            else:
                self.lock_screen.destroy()
                self.setup_ui()
                self.apply_theme()
                self.load_secrets()

    def ask_password(self, title, prompt):
        return PasswordDialog(self.root, title, prompt).show()

    def ask_password_for_secret(self, secret_name, action="просмотра"):
        return SecretPasswordDialog(
            self.root, secret_name, action, self.current_theme
        ).show()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.current_theme["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_frame = tk.Frame(main_frame, bg=self.current_theme["bg"])
        search_frame.pack(fill=tk.X, pady=(12, 8), padx=12)

        tk.Label(search_frame, text="Поиск:", bg=self.current_theme["bg"], fg=self.current_theme["fg"],
                 font=("Arial", 12)).pack(
            side=tk.LEFT, padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40,
                                     bg=self.current_theme["entry_bg"], fg=self.current_theme["entry_fg"],
                                     insertbackground=self.current_theme["cursor_color"],
                                     font=("Arial", 11))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 12))
        self.search_entry.bind('<KeyRelease>', self.on_search)

        btn_frame = tk.Frame(search_frame, bg=self.current_theme["bg"])
        btn_frame.pack(side=tk.RIGHT)

        buttons = [
            ("Добавить новый секрет", self.add_secret, 160),
            ("Обновить", self.load_secrets, 100),
            ("🌙 Тема", self.toggle_theme, 80),
            ("🚪 Выйти", self.exit_app, 80)
        ]

        for i, (text, command, width) in enumerate(buttons):
            btn = RoundedButton(btn_frame, text=text, command=command,
                                bg_color=self.current_theme["button_bg"],
                                fg_color=self.current_theme["button_fg"],
                                hover_color=self.current_theme["accent_hover"],
                                parent_bg_color=self.current_theme["bg"],
                                width=width, height=32, corner_radius=20)
            btn.grid(row=0, column=i, padx=(0, 6))

        content_frame = tk.Frame(main_frame, bg=self.current_theme["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        list_frame = tk.Frame(content_frame, bg=self.current_theme["bg"])
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(list_frame, text="Сохраненные секреты:", bg=self.current_theme["bg"],
                 fg=self.current_theme["fg"], font=("Arial", 12)).pack(anchor=tk.W)

        self.secrets_list = tk.Listbox(list_frame, width=50, height=15,
                                       bg=self.current_theme["listbox_bg"], fg=self.current_theme["listbox_fg"],
                                       font=("Arial", 11))
        self.secrets_list.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.secrets_list.bind('<<ListboxSelect>>', self.on_secret_select)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.secrets_list.yview,
                                 bg=self.current_theme["scrollbar_bg"],
                                 troughcolor=self.current_theme["scrollbar_trough"],
                                 activebackground=self.current_theme["scrollbar_active"])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.secrets_list.configure(yscrollcommand=scrollbar.set)

        details_frame = tk.LabelFrame(content_frame, text="Детали секрета", padx=12, pady=12,
                                      bg=self.current_theme["bg"], fg=self.current_theme["fg"],
                                      font=("Arial", 12))
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(12, 0))

        details_header = tk.Frame(details_frame, bg=self.current_theme["bg"])
        details_header.pack(fill=tk.X, pady=(0, 8))

        tk.Label(details_header, text="Детали:", bg=self.current_theme["bg"], fg=self.current_theme["fg"],
                 font=("Arial", 12)).pack(
            side=tk.LEFT)

        self.toggle_password_btn = tk.Button(
            details_header, text="👁 Показать пароль", bg=self.current_theme["button_bg"],
            fg=self.current_theme["button_fg"], command=self.toggle_password_visibility,
            font=("Arial", 11)
        )
        self.toggle_password_btn.pack(side=tk.RIGHT)
        self.password_visible = False

        self.details_text = tk.Text(details_frame, width=40, height=15, state=tk.DISABLED,
                                    bg=self.current_theme["text_bg"], fg=self.current_theme["text_fg"],
                                    insertbackground=self.current_theme["cursor_color"],
                                    font=("Arial", 11))
        self.details_text.pack(fill=tk.BOTH, expand=True)

        btn_frame2 = tk.Frame(main_frame, bg=self.current_theme["bg"])
        btn_frame2.pack(fill=tk.X, pady=12, padx=12)

        action_buttons = [
            ("Копировать данные подключения", self.copy_connection_string, 220),
            ("Удалить выбранный", self.delete_secret, 150),
            ("Показать подключение к БД", self.show_db_connection, 180)
        ]

        for i, (text, command, width) in enumerate(action_buttons):
            btn = RoundedButton(btn_frame2, text=text, command=command,
                                bg_color=self.current_theme["button_bg"],
                                fg_color=self.current_theme["button_fg"],
                                hover_color=self.current_theme["accent_hover"],
                                parent_bg_color=self.current_theme["bg"],
                                width=width, height=32, corner_radius=20)
            btn.grid(row=0, column=i, padx=(0, 6))

        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN,
                              bg=self.current_theme["status_bg"], fg=self.current_theme["status_fg"],
                              font=("Arial", 11))
        status_bar.pack(fill=tk.X, padx=12, pady=(0, 12))

    def exit_app(self):
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти из приложения?"):
            self.root.destroy()

    def apply_theme(self):
        theme = self.current_theme
        self.root.configure(bg=theme["bg"])
        self.apply_theme_to_widget(self.root, theme)

    def apply_theme_to_widget(self, widget, theme):
        try:
            if isinstance(widget, tk.Entry):
                widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"],
                                 insertbackground=theme["cursor_color"])
            elif isinstance(widget, tk.Listbox):
                widget.configure(bg=theme["listbox_bg"], fg=theme["listbox_fg"])
            elif isinstance(widget, tk.Text):
                widget.configure(bg=theme["text_bg"], fg=theme["text_fg"],
                                 insertbackground=theme["cursor_color"])
            elif isinstance(widget, tk.Label):
                widget.configure(bg=theme["bg"], fg=theme["fg"])
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=theme["bg"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=theme["button_bg"], fg=theme["button_fg"])
            elif isinstance(widget, tk.Scrollbar):
                widget.configure(bg=theme["scrollbar_bg"], troughcolor=theme["scrollbar_trough"])
            elif isinstance(widget, tk.LabelFrame):
                widget.configure(bg=theme["bg"], fg=theme["fg"])
        except:
            pass

        for child in widget.winfo_children():
            self.apply_theme_to_widget(child, theme)

    def toggle_theme(self):
        self.current_theme = self.theme_manager.toggle_theme()
        self.apply_theme()
        self.load_secrets()

    def load_secrets(self, search_term=None):
        if search_term is None:
            search_term = self.search_var.get()

        secrets = self.db.search_secrets(search_term)
        self.secrets_list.delete(0, tk.END)

        for secret in secrets:
            self.secrets_list.insert(tk.END, secret)

        count = len(secrets)
        if count == 0 and search_term:
            self.status_var.set(f"❌ Секрет '{search_term}' не найден")
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, f"❌ Секрет '{search_term}' не найден")
            self.details_text.config(state=tk.DISABLED)
        elif search_term:
            self.status_var.set(f"Найдено {count} секретов по запросу '{search_term}'")
        else:
            self.status_var.set(f"Загружено {count} секретов")

    def on_search(self, event=None):
        self.load_secrets()

    def add_secret(self):
        dialog = AddSecretDialog(self.root, self.current_theme)
        if dialog.result:
            name, secret_data = dialog.result

            master_password = self.ask_password_for_secret(name, "сохранения")
            if not master_password or not self.db.verify_master_password(master_password):
                messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
                return

            if self.db.save_secret(name, secret_data, master_password):
                messagebox.showinfo("Успех", f"Секрет '{name}' успешно сохранен!")
                self.load_secrets()
                self.status_var.set(f"Секрет '{name}' сохранен")

    def on_secret_select(self, event=None):
        selection = self.secrets_list.curselection()
        if not selection:
            return

        secret_name = self.secrets_list.get(selection[0])
        self.show_secret_details(secret_name)

    def show_secret_details(self, secret_name):
        self.password_visible = False
        self.toggle_password_btn.config(text="👁 Показать пароль")

        master_password = self.ask_password_for_secret(secret_name, "просмотра")
        if not master_password or not self.db.verify_master_password(master_password):
            messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
            return

        secret_data = self.db.get_secret(secret_name, master_password)
        if secret_data is None:
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, f"❌ Секрет '{secret_name}' не найден")
            self.details_text.config(state=tk.DISABLED)
            self.status_var.set(f"Секрет '{secret_name}' не найден")
            return

        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)

        details = f"🔐 {secret_name}\n" + "=" * 40 + "\n\n"
        details += f"📍 Хост: {secret_data.get('host', 'N/A')}\n"
        details += f"👤 Логин: {secret_data.get('username', 'N/A')}\n"
        details += f"🔑 Пароль: {'*' * len(secret_data.get('password', ''))}\n"
        details += f"📊 Тип: {secret_data.get('type', 'Database')}\n"

        self.details_text.insert(1.0, details)
        self.details_text.config(state=tk.DISABLED)

        self.current_secret_name = secret_name
        self.current_secret_data = secret_data
        self.status_var.set(f"Загружен секрет: {secret_name}")

    def toggle_password_visibility(self):
        if not self.current_secret_name:
            return

        if self.password_visible:
            self.show_secret_details(self.current_secret_name)
            self.toggle_password_btn.config(text="👁 Показать пароль")
            self.password_visible = False
        else:
            master_password = self.ask_password_for_secret(self.current_secret_name, "просмотра пароля")
            if not master_password or not self.db.verify_master_password(master_password):
                messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
                return

            secret_data = self.db.get_secret(self.current_secret_name, master_password)
            if secret_data is None:
                return

            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)

            details = f"🔐 {self.current_secret_name}\n" + "=" * 40 + "\n\n"
            details += f"📍 Хост: {secret_data.get('host', 'N/A')}\n"
            details += f"👤 Логин: {secret_data.get('username', 'N/A')}\n"
            details += f"🔑 Пароль: {secret_data.get('password', '')}\n"
            details += f"📊 Тип: {secret_data.get('type', 'Database')}\n"

            self.details_text.insert(1.0, details)
            self.details_text.config(state=tk.DISABLED)

            self.toggle_password_btn.config(text="🙈 Скрыть пароль")
            self.password_visible = True

    def copy_connection_string(self):
        if not hasattr(self, 'current_secret_name') or not self.current_secret_name:
            messagebox.showwarning("Предупреждение", "Сначала выберите секрет")
            return

        master_password = self.ask_password_for_secret(self.current_secret_name, "доступа к")
        if not master_password or not self.db.verify_master_password(master_password):
            messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
            return

        secret_data = self.db.get_secret(self.current_secret_name, master_password)
        if not secret_data:
            messagebox.showerror("Ошибка", "Не удалось получить данные секрета")
            return

        conn_string = f"host={secret_data.get('host', '')} port={secret_data.get('port', '')} "
        conn_string += f"dbname={secret_data.get('database', '')} user={secret_data.get('username', '')} "
        conn_string += f"password={secret_data.get('password', '')}"

        self.root.clipboard_clear()
        self.root.clipboard_append(conn_string)
        self.status_var.set(f"Строка подключения скопирована для {self.current_secret_name}")
        messagebox.showinfo("Успех", "Строка подключения скопирована в буфер обмена!")

    def delete_secret(self):
        selection = self.secrets_list.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Сначала выберите секрет для удаления")
            return

        secret_name = self.secrets_list.get(selection[0])

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить секрет '{secret_name}'?"):
            master_password = self.ask_password_for_secret(secret_name, "удаления")
            if not master_password or not self.db.verify_master_password(master_password):
                messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
                return

            self.db.delete_secret(secret_name)
            self.load_secrets()
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.config(state=tk.DISABLED)
            self.status_var.set(f"Секрет '{secret_name}' удален")
            messagebox.showinfo("Успех", f"Секрет '{secret_name}' удален")

    def show_db_connection(self):
        if not hasattr(self, 'current_secret_name') or not self.current_secret_name:
            messagebox.showwarning("Предупреждение", "Сначала выберите секрет")
            return

        master_password = self.ask_password_for_secret(self.current_secret_name, "просмотра")
        if not master_password or not self.db.verify_master_password(master_password):
            messagebox.showerror("Ошибка", "Неверный мастер-пароль!")
            return

        secret_data = self.db.get_secret(self.current_secret_name, master_password)
        if not secret_data:
            messagebox.showerror("Ошибка", "Не удалось получить данные секрета")
            return

        conn_info = f"Подключение к БД:\n\n"
        conn_info += f"Хост: {secret_data.get('host', 'N/A')}\n"
        conn_info += f"Логин: {secret_data.get('username', 'N/A')}\n"
        conn_info += f"Пароль: {secret_data.get('password', 'N/A')}"

        messagebox.showinfo(f"Подключение: {self.current_secret_name}", conn_info)




def main():


    root = tk.Tk()
    app = SecretWallet(root)
    root.mainloop()


if __name__ == "__main__":
    main()