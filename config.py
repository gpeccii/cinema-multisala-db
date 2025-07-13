import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:

	DB_HOST = os.getenv('DB_HOST', 'localhost')
	DB_PORT = os.getenv('DB_PORT', '3306')
	DB_NAME = os.getenv('DB_NAME', 'cinema_multisala')
	DB_USER = os.getenv('DB_USER', 'root')
	DB_PASSWORD = os.getenv('DB_PASSWORD', '')

	SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

	SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
	SQLALCHEMY_POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE', '5'))
	SQLALCHEMY_MAX_OVERFLOW = int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', '10'))

class AppConfig:

	APP_NAME = "Cinema Multisala Management System"
	APP_VERSION = "1.0.0"
	APP_DESCRIPTION = "Sistema di gestione per cinema multisala - E-tivity 4"

	ITEMS_PER_PAGE = 10
	DATE_FORMAT = "%Y-%m-%d"
	TIME_FORMAT = "%H:%M"
	DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
