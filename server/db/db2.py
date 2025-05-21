from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

USER = os.getenv("PG_USER")
PASSWORD = os.getenv("PG_PASS")
HOST = os.getenv("PG_HOST")
PORT = os.getenv("PG_PORT")
DBNAME = os.getenv("PG_DATABASE")

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

engine = create_engine(DATABASE_URL, poolclass=NullPool)

# test
try:
    with engine.connect() as connection:
        print("Connected to supabase!")
except Exception as e:
    print(f"Failed to connect to supabase: {e}")