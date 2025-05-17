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
                path TEXT UNIQUE NOT NULL,
                image_name TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patient(id) ON UPDATE CASCADE ON DELETE SET NULL
            )""")


        # Insert dummy doctors if table is empty
        self.cursor.execute("SELECT COUNT(*) FROM doctor")
        if self.cursor.fetchone()[0] == 0:
            dummy_doctors = ['Dr. House', 'Dr. Strange', 'Dr. Who', 'Dr. Watson', 'Dr. Doom']
            for name in dummy_doctors:
                self.cursor.execute("INSERT INTO doctor (name) VALUES (?)", (name,))

        # Insert dummy patients if table is empty
        self.cursor.execute("SELECT COUNT(*) FROM patient")
        if self.cursor.fetchone()[0] == 0:
            # Assign each patient to a different doctor (1-5)
            dummy_patients = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
            for i, name in enumerate(dummy_patients):
                doctor_id = i + 1  # Assuming IDs autoincrement from 1
                self.cursor.execute("INSERT INTO patient (name, doctor_id) VALUES (?, ?)", (name, doctor_id))


        self.connection.commit()

    def close(self):
        self.connection.close()
        Database._instance = None
