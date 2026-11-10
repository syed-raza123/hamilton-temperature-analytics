
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Locate the project root
project_root = Path(__file__).resolve().parent.parent

# Load database credentials
load_dotenv(project_root / ".env")

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# Check that required credentials exist
required = {
    "DB_HOST": db_host,
    "DB_PORT": db_port,
    "DB_NAME": db_name,
    "DB_USER": db_user,
    "DB_PASSWORD": db_password
}

missing = [key for key, value in required.items() if not value]

if missing:
    print("Missing environment variables:", ", ".join(missing))

else:
    try:
        with psycopg.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=5
        ) as connection:

            print("SUCCESS: Connected to PostgreSQL!")

            # Execute a safe read-only query
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database();")

                database_name = cursor.fetchone()[0]

                print("Connected database:", database_name)

    except psycopg.Error as error:
        print("ERROR: PostgreSQL connection failed.")
        print(type(error).__name__)
        print(str(error))
