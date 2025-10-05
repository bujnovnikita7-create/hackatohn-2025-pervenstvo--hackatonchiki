import tkinter as tk
from tkinter import messagebox
from database import Database
from dialogs import PasswordDialog, SecretPasswordDialog, AddSecretDialog
from ui_components import LockScreen, Theme, RoundedButton


class SecretWallet:
    # Главный класс приложения - хранилище секретов

    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Storage of Secrets")

        # Устанавливаем черный фон сразу
        self.root.configure(bg='black')

        # Попытка загрузки иконки приложения
        try:
            self.root.iconphoto(True, tk.PhotoImage(file="Hakaton_image.png"))
        except:
            try:
                self.root.iconphoto(True, tk.PhotoImage(file="Hakaton_image.jpg"))
            except:
                # Иконка не загружена - приложение продолжит работу без нее
                pass

        self.root.state('zoomed')
        self.db = Database()
        self.current_secret_name = None
        self.current_secret_data = None
        self.theme_manager = Theme()
        self.current_theme = self.theme_manager.get_theme()

        # Создаем экран блокировки и форсируем отрисовку
        self.lock_screen = LockScreen(root)
        self.root.update()  # Форсируем обновление интерфейса

        self.verify_master_password_on_startup()

    def verify_master_password_on_startup(self):
        # Проверка и установка мастер-пароля при запуске
        if not self.db.is_master_password_set():
            # Даем время на отрисовку экрана блокировки
            self.root.after(100, self._setup_master_password)
        else:
            self.root.after(100, self._verify_master_password)

    def _setup_master_password(self):
        # Настройка мастер-пароля
        self.lock_screen.destroy()
        messagebox.showinfo("Настройка", "Установите мастер-пароль для защиты ваших секретов.")
        self._setup_master_password_loop()

    def _setup_master_password_loop(self):
        # Цикл установки мастер-пароля
        password = self.ask_password("Установка мастер-пароля", "Введите новый мастер-пароль:")
        if not password:
            if messagebox.askyesno("Подтверждение",
                                   "Без мастер-пароля вы не сможете сохранять секреты. Вы уверены?"):
                self.root.destroy()
                return
            self._setup_master_password_loop()
            return

        confirm = self.ask_password("Подтверждение", "Повторите мастер-пароль:")

        if password == confirm:
            if self.db.set_master_password(password):
                messagebox.showinfo("Успех", "Мастер-пароль успешно установлен!")
                self.setup_ui()
                self.apply_theme()
                self.load_secrets()
            else:
                messagebox.showerror("Ошибка", "Не удалось установить мастер-пароль")
                self._setup_master_password_loop()
        else:
            messagebox.showerror("Ошибка", "Пароли не совпадают. Попробуйте снова.")
            self._setup_master_password_loop()

    def _verify_master_password(self):
        # Проверка существующего мастер-пароля
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
        # Запрос пароля через диалоговое окно
        return PasswordDialog(self.root, title, prompt).show()

    def ask_password_for_secret(self, secret_name, action="просмотра"):
        # Запрос пароля для работы с конкретным секретом
        return SecretPasswordDialog(
            self.root, secret_name, action, self.current_theme
        ).show()

    def setup_ui(self):
        # Настройка пользовательского интерфейса
        main_frame = tk.Frame(self.root, bg=self.current_theme["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Панель поиска
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

        # Панель кнопок управления
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

        # Основная область контента
        content_frame = tk.Frame(main_frame, bg=self.current_theme["bg"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Левая панель - список секретов
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

        # Правая панель - детали секрета
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

        # Панель действий
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

        # Строка состояния
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN,
                              bg=self.current_theme["status_bg"], fg=self.current_theme["status_fg"],
                              font=("Arial", 11))
        status_bar.pack(fill=tk.X, padx=12, pady=(0, 12))

    def exit_app(self):
        # Выход из приложения
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти из приложения?"):
            self.root.destroy()

    def apply_theme(self):
        # Применение текущей темы ко всем элементам интерфейса
        theme = self.current_theme
        self.root.configure(bg=theme["bg"])
        self.apply_theme_to_widget(self.root, theme)

    def apply_theme_to_widget(self, widget, theme):
        # Рекурсивное применение темы к виджету и его дочерним элементам
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
        # Переключение между темами оформления
        self.current_theme = self.theme_manager.toggle_theme()
        self.apply_theme()
        self.load_secrets()

    def load_secrets(self, search_term=None):
        # Загрузка и отображение списка секретов
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
        # Обработчик поиска секретов
        self.load_secrets()

    def add_secret(self):
        # Добавление нового секрета
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
        # Обработчик выбора секрета из списка
        selection = self.secrets_list.curselection()
        if not selection:
            return

        secret_name = self.secrets_list.get(selection[0])
        self.show_secret_details(secret_name)

    def show_secret_details(self, secret_name):
        # Отображение деталей выбранного секрета
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
        # Переключение видимости пароля в деталях секрета
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
        # Копирование строки подключения в буфер обмена
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
        # Удаление выбранного секрета
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
        # Отображение информации о подключении к БД
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