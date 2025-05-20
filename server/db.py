import sqlite3
<<<<<<< HEAD

class db:
    _instance = None
=======
import threading

class Database:
    _instance = None
    _lock = threading.Lock()
>>>>>>> 56ef03b054e28f84c6d7d26306f4a1c4e262e822

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
<<<<<<< HEAD
                    cls._instance = super(db, cls).__new__(cls)
                    cls._instance._init_db()
        return cls._instance

    def connect_db(self):
        self.connection = sqlite3.connect('database.db')
=======
                    cls._instance = super(Database, cls).__new__(cls)
                    cls._instance._connect_db()
                    cls._instance._init_db()
        return cls._instance

    def _connect_db(self):
        self.connection = sqlite3.connect('database.db', check_same_thread=False)
>>>>>>> 56ef03b054e28f84c6d7d26306f4a1c4e262e822
        self.cursor = self.connection.cursor()

    def get_connection(self):
        return self.connection

    def get_cursor(self):
        return self.cursor

<<<<<<< HEAD
    def __init_db(self):
=======
    def _init_db(self):
>>>>>>> 56ef03b054e28f84c6d7d26306f4a1c4e262e822
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS doctor(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
<<<<<<< HEAD
                )""")
=======
            )""")
>>>>>>> 56ef03b054e28f84c6d7d26306f4a1c4e262e822

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS patient(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                doctor_id INTEGER,
                FOREIGN KEY (doctor_id) REFERENCES doctor(id) ON UPDATE CASCADE ON DELETE SET NULL
<<<<<<< HEAD
                )""")
=======
            )""")
>>>>>>> 56ef03b054e28f84c6d7d26306f4a1c4e262e822

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS images(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
<<<<<<< HEAD
                image_id TEXT UNIQUE NOT NULL,
                image_name TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patient(id) ON UPDATE CASCADE ON DELETE SET NULL
                )""")


    def close(self):
        self.connection.close()
        db._instance = None
=======
                path TEXT UNIQUE NOT NULL,
                image_name TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patient(id) ON UPDATE CASCADE ON DELETE SET NULL
            )""")


        self.cursor.execute("SELECT COUNT(*) FROM doctor")
        if self.cursor.fetchone()[0] == 0:
            dummy_doctors = ['Dr. House', 'Dr. Strange', 'Dr. Who', 'Dr. Watson', 'Dr. Doom']
            for name in dummy_doctors:
                self.cursor.execute("INSERT INTO doctor (name) VALUES (?)", (name,))

        self.cursor.execute("SELECT COUNT(*) FROM patient")
        if self.cursor.fetchone()[0] == 0:
            dummy_patients = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
            for i, name in enumerate(dummy_patients):
                self.cursor.execute("INSERT INTO patient (name, doctor_id) VALUES (?, ?)", (name, doctor_id))


        self.connection.commit()

    def close(self):
        self.connection.close()
        Database._instance = None
>>>>>>> 56ef03b054e28f84c6d7d26306f4a1c4e262e822
