from dotenv import load_dotenv
load_dotenv()

import os


class Config:
    class Database:
        host: str = os.environ.get('DB_HOST')
        port: str = os.environ.get('DB_PORT')
        dbname: str = os.environ.get('DB_NAME', 5432)
        user: str = os.environ.get('DB_USER')
        password: str = os.environ.get('DB_PASSWORD')
