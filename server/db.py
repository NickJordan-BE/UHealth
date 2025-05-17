import sqlite3

class db:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(db, cls).__new__(cls)
                    cls._instance._init_db()
        return cls._instance

    def connect_db(self):
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()

    def get_connection(self):
        return self.connection

    def get_cursor(self):
        return self.cursor

    def __init_db(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS doctor(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
                )""")

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS patient(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                doctor_id INTEGER,
                FOREIGN KEY (doctor_id) REFERENCES doctor(id) ON UPDATE CASCADE ON DELETE SET NULL
                )""")

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS images(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                image_id TEXT UNIQUE NOT NULL,
                image_name TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patient(id) ON UPDATE CASCADE ON DELETE SET NULL
                )""")


    def close(self):
        self.connection.close()
        db._instance = None