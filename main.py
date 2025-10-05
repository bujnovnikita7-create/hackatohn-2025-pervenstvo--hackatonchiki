import tkinter as tk
from app import SecretWallet


def main():
    try:

        root = tk.Tk()

        app = SecretWallet(root)

        root.mainloop()

    except Exception as e:

        print(f"Критическая ошибка при запуске приложения: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()
