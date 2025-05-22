# do not use me

import sqlite3
import threading

class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Database, cls).__new__(cls)
                    cls._instance._connect_db()
                    cls._instance._init_db()
        return cls._instance

    def _connect_db(self):
        self.connection = sqlite3.connect('database.db', check_same_thread=False)
        self.cursor = self.connection.cursor()

    def get_connection(self):
        return self.connection

    def get_cursor(self):
        return self.cursor

    def _init_db(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS doctor(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patient(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                doctor_id INTEGER,
                FOREIGN KEY (doctor_id) REFERENCES doctor(id) ON UPDATE CASCADE ON DELETE SET NULL
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS images(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                path TEXT UNIQUE NOT NULL,
                image_name TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patient(id) ON UPDATE CASCADE ON DELETE SET NULL
            )
            """
        )
        
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS diagnosis(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                diagnosis_name TEXT NOT NULL,
                patient_id INTEGER,
                doctor_id INTEGER,
                FOREIGN KEY (image_id) REFERENCES images(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (patient_id) REFERENCES patient(id) ON UPDATE CASCADE ON DELETE SET NULL,
                FOREIGN KEY (doctor_id) REFERENCES doctor(id) ON UPDATE CASCADE ON DELETE SET NULL
            )
            """
        )

        self.connection.commit()

    def close(self):
        self.connection.close()
        Database._instance = None
