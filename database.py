import os
import mysql.connector
from dotenv import load_dotenv   # <-- you need this import

# Load environment variables from .env file
load_dotenv()

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

print(os.getenv("DB_HOST"))
