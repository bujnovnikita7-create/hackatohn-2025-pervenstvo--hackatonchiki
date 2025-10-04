#Основной модуль приложения - хранилище секретов
import tkinter as tk
from tkinter import messagebox, simpledialog

from database import Database
from theme import Theme
from widgets import RoundedButton
from dialogs import AddSecretDialog


class SecretWallet:
    #Главное окно приложения - хранилище секретов

    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Хранилище секретов")
        self.root.geometry("800x600")

        self.db = Database()
        self.current_secret_name = None
        self.current_secret_data = None
        self.theme_manager = Theme()
        self.current_theme = self.theme_manager.get_theme()

        self.verify_master_password_on_startup()
        self.setup_ui()
        self.apply_theme()
        self.load_secrets()

    def verify_master_password_on_startup(self):
        #Проверка мастер-пароля при запуске
        if not self.db.is_master_password_set():
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

    def ask_password(self, title, prompt):
        #Кастомный диалог для ввода пароля без сворачивания окна
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.current_theme["bg_secondary"])

        # Центрирование диалога
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        result = [None]  # Используем список для передачи по ссылке

        tk.Label(dialog, text=prompt, bg=self.current_theme["bg_secondary"],
                 fg=self.current_theme["fg"], wraplength=280).pack(pady=10)

        password_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=password_var, show='*',
                         bg=self.current_theme["entry_bg"], fg=self.current_theme["entry_fg"],
                         width=30)
        entry.pack(pady=5)
        entry.focus()

        def on_ok():
            result[0] = password_var.get()
            dialog.destroy()

        def on_cancel():
            result[0] = ""
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg=self.current_theme["bg_secondary"])
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="OK", command=on_ok,
                  bg=self.current_theme["button_bg"], fg=self.current_theme["button_fg"]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=on_cancel,
                  bg=self.current_theme["button_bg"], fg=self.current_theme["button_fg"]).pack(side=tk.LEFT, padx=5)

        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())

        self.root.wait_window(dialog)
        return result[0]

    def ask_password_for_secret(self, secret_name, action="просмотра"):
        """Диалог для ввода пароля при работе с секретами"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Мастер-пароль")
        dialog.geometry("350x120")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.current_theme["bg_secondary"])

        # Центрирование диалога
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        result = [None]

        tk.Label(dialog, text=f"Введите мастер-пароль для {action} секрета '{secret_name}':",
                 bg=self.current_theme["bg_secondary"], fg=self.current_theme["fg"],
                 wraplength=330).pack(pady=10)

        password_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=password_var, show='*',
                         bg=self.current_theme["entry_bg"], fg=self.current_theme["entry_fg"],
                         width=30)
        entry.pack(pady=5)
        entry.focus()

        def on_ok():
            result[0] = password_var.get()
            dialog.destroy()

        def on_cancel():
            result[0] = ""
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg=self.current_theme["bg_secondary"])
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="OK", command=on_ok,
                  bg=self.current_theme["button_bg"], fg=self.current_theme["button_fg"]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=on_cancel,
                  bg=self.current_theme["button_bg"], fg=self.current_theme["button_fg"]).pack(side=tk.LEFT, padx=5)

        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())

        self.root.wait_window(dialog)
        return result[0]

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # ... (остальной код setup_ui без изменений)
        main_frame = tk.Frame(self.root, bg=self.current_theme["bg"])
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Search frame
        search_frame = tk.Frame(main_frame, bg=self.current_theme["bg"])
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        tk.Label(search_frame, text="Поиск:", bg=self.current_theme["bg"], fg=self.current_theme["fg"]).grid(
            row=0, column=0, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40,
                                     bg=self.current_theme["entry_bg"], fg=self.current_theme["entry_fg"])
        self.search_entry.grid(row=0, column=1, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)

        btn_frame = tk.Frame(search_frame, bg=self.current_theme["bg"])
        btn_frame.grid(row=0, column=2)

        buttons = [
            ("Добавить новый секрет", self.add_secret, 160),
            ("Обновить", self.load_secrets, 100),
            ("🌙 Тема", self.toggle_theme, 80)
        ]

        for i, (text, command, width) in enumerate(buttons):
            btn = RoundedButton(btn_frame, text=text, command=command,
                                bg_color=self.current_theme["button_bg"],
                                fg_color=self.current_theme["button_fg"],
                                hover_color=self.current_theme["accent_hover"],
                                parent_bg_color=self.current_theme["bg"],
                                width=width, height=30, corner_radius=20)
            btn.grid(row=0, column=i, padx=(0, 5))

        # List frame
        list_frame = tk.Frame(main_frame, bg=self.current_theme["bg"])
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        tk.Label(list_frame, text="Сохраненные секреты:", bg=self.current_theme["bg"],
                 fg=self.current_theme["fg"]).grid(
            row=0, column=0, sticky=tk.W)

        self.secrets_list = tk.Listbox(list_frame, width=50, height=15,
                                       bg=self.current_theme["listbox_bg"], fg=self.current_theme["listbox_fg"])
        self.secrets_list.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.secrets_list.bind('<Double-Button-1>', self.on_secret_select)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.secrets_list.yview,
                                 bg=self.current_theme["scrollbar_bg"],
                                 troughcolor=self.current_theme["scrollbar_trough"],
                                 activebackground=self.current_theme["scrollbar_active"])
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.secrets_list.configure(yscrollcommand=scrollbar.set)

        # Details frame
        details_frame = tk.LabelFrame(main_frame, text="Детали секрета", padx=10, pady=10,
                                      bg=self.current_theme["bg"], fg=self.current_theme["fg"])
        details_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))

        self.details_text = tk.Text(details_frame, width=40, height=15, state=tk.DISABLED,
                                    bg=self.current_theme["text_bg"], fg=self.current_theme["text_fg"])
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Action buttons
        btn_frame2 = tk.Frame(main_frame, bg=self.current_theme["bg"])
        btn_frame2.grid(row=2, column=0, columnspan=2, pady=(10, 0))

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
                                width=width, height=30, corner_radius=20)
            btn.grid(row=0, column=i, padx=(0, 5))

        # Status bar
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN,
                              bg=self.current_theme["status_bg"], fg=self.current_theme["status_fg"])
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        list_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
        details_frame.columnconfigure(0, weight=1)

    def apply_theme(self):
        """Применение текущей темы ко всем виджетам"""
        theme = self.current_theme
        self.root.configure(bg=theme["bg"])
        self.apply_theme_to_widget(self.root, theme)

    def apply_theme_to_widget(self, widget, theme):
        """Рекурсивное применение темы к виджету и его дочерним элементам"""
        try:
            if isinstance(widget, tk.Entry):
                widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
            elif isinstance(widget, tk.Listbox):
                widget.configure(bg=theme["listbox_bg"], fg=theme["listbox_fg"])
            elif isinstance(widget, tk.Text):
                widget.configure(bg=theme["text_bg"], fg=theme["text_fg"], insertbackground=theme["fg"])
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
        """Переключение темы оформления"""
        self.current_theme = self.theme_manager.toggle_theme()
        self.apply_theme()
        self.load_secrets()

    def load_secrets(self, search_term=None):
        """Загрузка списка секретов"""
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
        """Обработчик поиска"""
        self.load_secrets()

    def add_secret(self):
        """Добавление нового секрета"""
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
        """Обработчик выбора секрета"""
        selection = self.secrets_list.curselection()
        if not selection:
            return

        secret_name = self.secrets_list.get(selection[0])
        self.show_secret_details(secret_name)

    def show_secret_details(self, secret_name):
        """Показать детали выбранного секрета"""
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
        details += f"🚪 Порт: {secret_data.get('port', 'N/A')}\n"
        details += f"🗃️ База данных: {secret_data.get('database', 'N/A')}\n"
        details += f"👤 Логин: {secret_data.get('username', 'N/A')}\n"
        details += f"🔑 Пароль: {'*' * len(secret_data.get('password', ''))}\n"
        details += f"📊 Тип: {secret_data.get('type', 'Database')}\n"

        self.details_text.insert(1.0, details)
        self.details_text.config(state=tk.DISABLED)

        self.current_secret_name = secret_name
        self.current_secret_data = secret_data
        self.status_var.set(f"Загружен секрет: {secret_name}")

    def copy_connection_string(self):
        """Копирование строки подключения"""
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

        conn_string = f"host={secret_data.get('host', '')} port={secret_data.get('port', '')} " \
                      f"dbname={secret_data.get('database', '')} user={secret_data.get('username', '')} " \
                      f"password={secret_data.get('password', '')}"

        messagebox.showinfo("Данные подключения", f"Скопируйте строку подключения:\n\n{conn_string}")
        self.status_var.set("Данные подключения показаны для копирования")

    def show_db_connection(self):
        """Показать демонстрацию подключения к БД"""
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

        demo_text = f"""🎯 ДЕМОНСТРАЦИЯ ПОДКЛЮЧЕНИЯ К БД

1. Откройте ваш клиент БД
2. Создайте новое подключение
3. Используйте параметры:

   📍 Хост: {secret_data.get('host', 'N/A')}
   🚪 Порт: {secret_data.get('port', 'N/A')}
   🗃️ База данных: {secret_data.get('database', 'N/A')}
   👤 Пользователь: {secret_data.get('username', 'N/A')}
   🔑 Пароль: {secret_data.get('password', '')}

✅ Подключение должно быть успешным!"""

        messagebox.showinfo("Демо: Подключение к БД", demo_text)

    def delete_secret(self):
        """Удаление выбранного секрета"""
        selection = self.secrets_list.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите секрет для удаления")
            return

        secret_name = self.secrets_list.get(selection[0])

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить секрет '{secret_name}'?"):
            self.db.delete_secret(secret_name)
            self.load_secrets()
            self.status_var.set(f"Секрет '{secret_name}' удален")
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.config(state=tk.DISABLED)
            self.current_secret_name = None
            self.current_secret_data = None