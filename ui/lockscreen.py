import tkinter as tk


class LockScreen:
    #Экран блокировки с замком

    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_lock()

        self.canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        #Перерисовываем замок при изменении размера окна
        self.draw_lock()

    def draw_lock(self):
        #Рисует белый замок на черном фоне
        self.canvas.delete("all")
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        if width <= 1 or height <= 1:
            width = 800
            height = 600

        center_x = width // 2
        center_y = height // 2
        size = min(width, height) // 4

        self.canvas.create_rectangle(
            center_x - size // 2, center_y - size // 3,
            center_x + size // 2, center_y + size // 3,
            outline="white", width=3, fill="black"
        )

        self.canvas.create_arc(
            center_x - size // 3, center_y - size // 2,
            center_x + size // 3, center_y - size // 6,
            start=0, extent=180, outline="white", width=3, style=tk.ARC
        )

        self.canvas.create_text(
            center_x, center_y + size // 2 + 30,
            text="Введите мастер-пароль для доступа",
            fill="white", font=("Arial", 14)
        )

    def destroy(self):
        #Удаляет экран блокировки
        self.canvas.destroy()