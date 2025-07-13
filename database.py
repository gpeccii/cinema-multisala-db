from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging
from typing import Generator

from config import DatabaseConfig
from models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:

	def __init__(self):
		self.engine = None
		self.SessionLocal = None
		self._initialize_database()

	def _initialize_database(self):
		try:
			self.engine = create_engine(
				DatabaseConfig.SQLALCHEMY_DATABASE_URL,
				echo=DatabaseConfig.SQLALCHEMY_ECHO,
				pool_size=DatabaseConfig.SQLALCHEMY_POOL_SIZE,
				max_overflow=DatabaseConfig.SQLALCHEMY_MAX_OVERFLOW
			)

			self.SessionLocal = sessionmaker(
				autocommit=False,
				autoflush=False,
				bind=self.engine
			)

			self.test_connection()

			logger.info("Database inizializzato correttamente")

		except Exception as e:
			logger.error(f"Errore nell'inizializzazione del database: {e}")
			raise

	def test_connection(self):
		try:
			with self.engine.connect() as connection:
				result = connection.execute(text("SELECT 1"))
				logger.info("Connessione al database verificata")
				return True
		except Exception as e:
			logger.error(f"Errore nella connessione al database: {e}")
			raise

	def create_tables(self):
		try:
			Base.metadata.create_all(bind=self.engine)
			logger.info("Tabelle create con successo")
		except Exception as e:
			logger.error(f"Errore nella creazione delle tabelle: {e}")
			raise

	def drop_tables(self):
		try:
			Base.metadata.drop_all(bind=self.engine)
			logger.info("Tabelle eliminate con successo")
		except Exception as e:
			logger.error(f"Errore nell'eliminazione delle tabelle: {e}")
			raise

	@contextmanager
	def get_session(self) -> Generator[Session, None, None]:
		session = self.SessionLocal()
		try:
			yield session
			session.commit()
		except Exception as e:
			session.rollback()
			logger.error(f"Errore nella sessione database: {e}")
			raise
		finally:
			session.close()

	def get_session_direct(self) -> Session:
		return self.SessionLocal()

	def execute_raw_sql(self, sql_query: str, params: dict = None):
		try:
			with self.engine.connect() as connection:
				result = connection.execute(text(sql_query), params or {})
				connection.commit()
				return result
		except Exception as e:
			logger.error(f"Errore nell'esecuzione della query: {e}")
			raise

# Istanza globale del database manager
db_manager = DatabaseManager()

def get_db() -> Generator[Session, None, None]:
	with db_manager.get_session() as session:
		yield session

def init_database():
	try:
		db_manager.create_tables()
		logger.info("Database inizializzato con successo")
	except Exception as e:
		logger.error(f"Errore nell'inizializzazione: {e}")
		raise

def reset_database():
	try:
		db_manager.drop_tables()
		db_manager.create_tables()
		logger.info("Database resettato con successo")
	except Exception as e:
		logger.error(f"Errore nel reset del database: {e}")
		raise
