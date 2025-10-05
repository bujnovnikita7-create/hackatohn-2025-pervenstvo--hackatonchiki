import sqlite3
import json
from datetime import datetime
import base64
import os
import hashlib


class Database:
    #Управление базой данных секретов

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