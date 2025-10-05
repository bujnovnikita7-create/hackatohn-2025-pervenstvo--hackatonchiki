import tkinter as tk


class LockScreen:
    # Экран блокировки с анимированным замком

    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_lock()
        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        # Перерисовка замка при изменении размера окна
        self.draw_lock()

    def draw_lock(self):
        # Отрисовка графического замка
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
        # Создание прямоугольника со скругленными углами
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
        # Уничтожение экрана блокировки
        self.canvas.destroy()


class Theme:
    # Управление темами оформления приложения

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
        # Получение текущей темы
        return self.themes[self.current_theme]

    def toggle_theme(self):
        # Переключение между светлой и темной темой
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        return self.get_theme()


class RoundedButton(tk.Canvas):
    # Кастомная кнопка со скругленными углами

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
        # Отрисовка кнопки
        self.delete("all")
        self.configure(bg=self.parent_bg_color)
        self.create_rounded_rect(0, 0, self.width, self.height, self.corner_radius,
                                 fill=self.current_color, outline="")
        self.create_text(self.width // 2, self.height // 2, text=self.text,
                         fill=self.fg_color, font=("Arial", 11))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        # Создание скругленного прямоугольника
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1,
            x2, y1 + radius, x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2, x1, y2,
            x1, y2 - radius, x1, y1 + radius, x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _on_click(self, event):
        # Обработчик клика по кнопке
        if self.command:
            self.command()

    def _on_enter(self, event):
        # Обработчик наведения курсора
        self.current_color = self.hover_color
        self.draw_button()

    def _on_leave(self, event):
        # Обработчик ухода курсора
        self.current_color = self.bg_color
        self.draw_button()