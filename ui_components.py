import tkinter as tk


class LockScreen:
    def __init__(self, root):
        self.root = root
        # Изменен фон на серый (#2f3136) вместо черного
        self.frame = tk.Frame(root, bg="#2f3136")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Текст с инструкцией
        label = tk.Label(self.frame, text="Введите мастер-пароль для доступа",
                         bg="#2f3136", fg="white", font=("Arial", 16, "bold"))
        label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def destroy(self):
        self.frame.destroy()


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
                         fill=self.fg_color, font=("Arial", 10))  # Уменьшен шрифт для лучшего размещения

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
