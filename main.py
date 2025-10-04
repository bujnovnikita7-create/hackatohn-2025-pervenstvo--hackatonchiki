import tkinter as tk
from database import Database
from theme import Theme
from dialogs import AddSecretDialog
from wallet import SecretWallet
import sqlite3


def create_test_database():
    try:
        conn = sqlite3.connect('test_production.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('DELETE FROM users')
        cursor.execute('''
            INSERT INTO users (username, email) VALUES
            ('alice', 'alice@example.com'),
            ('bob', 'bob@company.org'),
            ('charlie', 'charlie.developer@test.io')
        ''')

        conn.commit()
        conn.close()
        print("✅ Тестовая БД создана успешно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при создании тестовой БД: {e}")
        return False


def main():
    print("🔐 Запуск Хранилище секретов")
    print("=" * 50)

    create_test_database()

    root = tk.Tk()
    app = SecretWallet(root)

    print("✅ Приложение запущено успешно!")
    root.mainloop()


if __name__ == "__main__":
    main()
