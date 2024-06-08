from dotenv import load_dotenv

from os import getenv

load_dotenv()

DB_USER = getenv('DB_USER')
DB_PASSWORD = getenv('DB_PASSWORD')
DB_NAME = getenv('DB_NAME')