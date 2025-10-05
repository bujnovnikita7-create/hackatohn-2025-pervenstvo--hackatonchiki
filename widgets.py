import tkinter as tk


class RoundedButton(tk.Canvas):
    #Кастомная кнопка с закругленными краями

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
                         fill=self.fg_color, font=("Arial", 10))

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