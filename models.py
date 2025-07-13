from sqlalchemy import Column, Integer, String, Text, Date, Time, DateTime, DECIMAL, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date, time

Base = declarative_base()

class Regista(Base):
	__tablename__ = 'REGISTA'

	ID_Regista = Column(Integer, primary_key=True, autoincrement=True)
	Nome_Regista = Column(String(50), nullable=False)
	Cognome_Regista = Column(String(50), nullable=False)
	Nazionalita = Column(String(50))
	Data_Nascita = Column(Date)

	film = relationship("Film", back_populates="regista")

	def __repr__(self):
		return f"<Regista(id={self.ID_Regista}, nome='{self.Nome_Regista} {self.Cognome_Regista}')>"

class TipoPromozione(Base):
	__tablename__ = 'TIPO_PROMOZIONE'

	ID_Tipo_Promozione = Column(Integer, primary_key=True, autoincrement=True)
	Nome_Tipo = Column(String(50), nullable=False)
	Descrizione_Tipo = Column(Text)

	promozioni = relationship("Promozione", back_populates="tipo_promozione")

	def __repr__(self):
		return f"<TipoPromozione(id={self.ID_Tipo_Promozione}, nome='{self.Nome_Tipo}')>"

class TipoTecnologia(Base):
	__tablename__ = 'TIPO_TECNOLOGIA'

	ID_Tecnologia = Column(Integer, primary_key=True, autoincrement=True)
	Nome_Tecnologia = Column(String(50), nullable=False)
	Descrizione_Tecnologia = Column(Text)

	sale = relationship("Supporta", back_populates="tecnologia")

	def __repr__(self):
		return f"<TipoTecnologia(id={self.ID_Tecnologia}, nome='{self.Nome_Tecnologia}')>"

class Film(Base):
	__tablename__ = 'FILM'

	ID_Film = Column(Integer, primary_key=True, autoincrement=True)
	Titolo = Column(String(100), nullable=False)
	Durata = Column(Integer, nullable=False)
	Genere = Column(String(50))
	Classificazione = Column(String(10))
	Anno_Uscita = Column(Integer)
	ID_Regista = Column(Integer, ForeignKey('REGISTA.ID_Regista'), nullable=False)

	regista = relationship("Regista", back_populates="film")
	proiezioni = relationship("Proiezione", back_populates="film")
	recensioni = relationship("Recensione", back_populates="film")

	def __repr__(self):
		return f"<Film(id={self.ID_Film}, titolo='{self.Titolo}', anno={self.Anno_Uscita})>"

class Sala(Base):
	__tablename__ = 'SALA'

	ID_Sala = Column(Integer, primary_key=True, autoincrement=True)
	Numero = Column(Integer, nullable=False, unique=True)
	Capienza = Column(Integer, nullable=False)
	Stato = Column(Enum('Attiva', 'Manutenzione', 'Fuori_Servizio'), default='Attiva')

	posti = relationship("Posto", back_populates="sala", cascade="all, delete-orphan")
	proiezioni = relationship("Proiezione", back_populates="sala")
	tecnologie = relationship("Supporta", back_populates="sala")

	def __repr__(self):
		return f"<Sala(id={self.ID_Sala}, numero={self.Numero}, capienza={self.Capienza})>"

class Posto(Base):
	__tablename__ = 'POSTO'

	ID_Posto = Column(Integer, primary_key=True, autoincrement=True)
	Numero_Posto = Column(Integer, nullable=False)
	Fila = Column(String(2), nullable=False)
	Stato_Posto = Column(Enum('Disponibile', 'Occupato', 'Manutenzione'), default='Disponibile')
	ID_Sala = Column(Integer, ForeignKey('SALA.ID_Sala'), nullable=False)

	__table_args__ = (UniqueConstraint('Numero_Posto', 'Fila', 'ID_Sala', name='unique_posto_sala'),)

	sala = relationship("Sala", back_populates="posti")
	biglietti = relationship("Biglietto", back_populates="posto")

	def __repr__(self):
		return f"<Posto(id={self.ID_Posto}, fila='{self.Fila}', numero={self.Numero_Posto})>"

class Tariffa(Base):
	__tablename__ = 'TARIFFA'

	ID_Tariffa = Column(Integer, primary_key=True, autoincrement=True)
	Nome_Tariffa = Column(String(50), nullable=False)
	Prezzo_Base = Column(DECIMAL(6,2), nullable=False)
	Fascia_Oraria = Column(Enum('Mattina', 'Pomeriggio', 'Sera', 'Notte'))
	Giorno_Settimana = Column(Enum('Lunedi', 'Martedi', 'Mercoledi', 'Giovedi', 'Venerdi', 'Sabato', 'Domenica'))
	Descrizione = Column(Text)

	proiezioni = relationship("Proiezione", back_populates="tariffa")

	def __repr__(self):
		return f"<Tariffa(id={self.ID_Tariffa}, nome='{self.Nome_Tariffa}', prezzo={self.Prezzo_Base})>"

class Operatore(Base):
	__tablename__ = 'OPERATORE'

	ID_Operatore = Column(Integer, primary_key=True, autoincrement=True)
	Nome = Column(String(50), nullable=False)
	Cognome = Column(String(50), nullable=False)
	Username = Column(String(50), nullable=False, unique=True)
	Password = Column(String(255), nullable=False)
	Ruolo = Column(Enum('Cassiere', 'Proiezionista', 'Manager', 'Tecnico'), nullable=False)

	proiezioni = relationship("Proiezione", back_populates="operatore")

	def __repr__(self):
		return f"<Operatore(id={self.ID_Operatore}, username='{self.Username}', ruolo='{self.Ruolo}')>"

class Cliente(Base):
	__tablename__ = 'CLIENTE'

	ID_Cliente = Column(Integer, primary_key=True, autoincrement=True)
	Nome = Column(String(50), nullable=False)
	Cognome = Column(String(50), nullable=False)
	Email = Column(String(100), nullable=False, unique=True)
	Telefono = Column(String(20))
	Data_Nascita = Column(Date)
	Data_Registrazione = Column(DateTime, default=func.current_timestamp())

	biglietti = relationship("Biglietto", back_populates="cliente")
	recensioni = relationship("Recensione", back_populates="cliente")

	def __repr__(self):
		return f"<Cliente(id={self.ID_Cliente}, nome='{self.Nome} {self.Cognome}', email='{self.Email}')>"

class Proiezione(Base):
	__tablename__ = 'PROIEZIONE'

	ID_Proiezione = Column(Integer, primary_key=True, autoincrement=True)
	Data = Column(Date, nullable=False)
	Ora_Inizio = Column(Time, nullable=False)
	Ora_Fine = Column(Time, nullable=False)
	ID_Film = Column(Integer, ForeignKey('FILM.ID_Film'), nullable=False)
	ID_Sala = Column(Integer, ForeignKey('SALA.ID_Sala'), nullable=False)
	ID_Operatore = Column(Integer, ForeignKey('OPERATORE.ID_Operatore'), nullable=False)
	ID_Tariffa = Column(Integer, ForeignKey('TARIFFA.ID_Tariffa'), nullable=False)

	__table_args__ = (UniqueConstraint('ID_Sala', 'Data', 'Ora_Inizio', name='unique_sala_orario'),)

	film = relationship("Film", back_populates="proiezioni")
	sala = relationship("Sala", back_populates="proiezioni")
	operatore = relationship("Operatore", back_populates="proiezioni")
	tariffa = relationship("Tariffa", back_populates="proiezioni")
	biglietti = relationship("Biglietto", back_populates="proiezione")

	def __repr__(self):
		return f"<Proiezione(id={self.ID_Proiezione}, data={self.Data}, ora={self.Ora_Inizio})>"

class Promozione(Base):
	__tablename__ = 'PROMOZIONE'

	ID_Promozione = Column(Integer, primary_key=True, autoincrement=True)
	Nome = Column(String(100), nullable=False)
	Descrizione = Column(Text)
	Percentuale_Sconto = Column(DECIMAL(5,2), nullable=False)
	Data_Inizio = Column(Date, nullable=False)
	Data_Fine = Column(Date, nullable=False)
	ID_Tipo_Promozione = Column(Integer, ForeignKey('TIPO_PROMOZIONE.ID_Tipo_Promozione'), nullable=False)

	tipo_promozione = relationship("TipoPromozione", back_populates="promozioni")
	biglietti = relationship("Biglietto", back_populates="promozione")

	def __repr__(self):
		return f"<Promozione(id={self.ID_Promozione}, nome='{self.Nome}', sconto={self.Percentuale_Sconto}%)>"

class Biglietto(Base):
	__tablename__ = 'BIGLIETTO'

	ID_Biglietto = Column(Integer, primary_key=True, autoincrement=True)
	Stato = Column(Enum('Valido', 'Utilizzato', 'Annullato'), default='Valido')
	Prezzo_Applicato = Column(DECIMAL(6,2), nullable=False)
	Data_Emissione = Column(DateTime, default=func.current_timestamp())
	ID_Proiezione = Column(Integer, ForeignKey('PROIEZIONE.ID_Proiezione'), nullable=False)
	ID_Cliente = Column(Integer, ForeignKey('CLIENTE.ID_Cliente'), nullable=False)
	ID_Promozione = Column(Integer, ForeignKey('PROMOZIONE.ID_Promozione'), nullable=True)
	ID_Posto = Column(Integer, ForeignKey('POSTO.ID_Posto'), nullable=False)

	__table_args__ = (UniqueConstraint('ID_Posto', 'ID_Proiezione', name='unique_posto_proiezione'),)

	proiezione = relationship("Proiezione", back_populates="biglietti")
	cliente = relationship("Cliente", back_populates="biglietti")
	promozione = relationship("Promozione", back_populates="biglietti")
	posto = relationship("Posto", back_populates="biglietti")

	def __repr__(self):
		return f"<Biglietto(id={self.ID_Biglietto}, prezzo={self.Prezzo_Applicato}, stato='{self.Stato}')>"

class Recensione(Base):
	__tablename__ = 'RECENSIONE'

	ID_Recensione = Column(Integer, primary_key=True, autoincrement=True)
	Valutazione = Column(Integer, nullable=False)
	Commento = Column(Text)
	Data_Recensione = Column(DateTime, default=func.current_timestamp())
	ID_Cliente = Column(Integer, ForeignKey('CLIENTE.ID_Cliente'), nullable=False)
	ID_Film = Column(Integer, ForeignKey('FILM.ID_Film'), nullable=False)

	__table_args__ = (UniqueConstraint('ID_Cliente', 'ID_Film', name='unique_cliente_film'),)

	cliente = relationship("Cliente", back_populates="recensioni")
	film = relationship("Film", back_populates="recensioni")

	def __repr__(self):
		return f"<Recensione(id={self.ID_Recensione}, valutazione={self.Valutazione}/10)>"

class Supporta(Base):
	__tablename__ = 'SUPPORTA'

	ID_Sala = Column(Integer, ForeignKey('SALA.ID_Sala'), primary_key=True)
	ID_Tecnologia = Column(Integer, ForeignKey('TIPO_TECNOLOGIA.ID_Tecnologia'), primary_key=True)

	sala = relationship("Sala", back_populates="tecnologie")
	tecnologia = relationship("TipoTecnologia", back_populates="sale")

	def __repr__(self):
		return f"<Supporta(sala_id={self.ID_Sala}, tecnologia_id={self.ID_Tecnologia})>"
