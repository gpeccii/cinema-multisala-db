from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
import logging
from models import *
from database import db_manager, reset_database
logger = logging.getLogger(__name__)

class CinemaOperations:
	def create_promozione(self, nome: str, tipo_promozione_id: int, percentuale_sconto: float, data_inizio, data_fine) -> int:
		with self.db.get_session() as session:
			promozione = Promozione(
				Nome=nome,
				ID_Tipo_Promozione=tipo_promozione_id,
				Percentuale_Sconto=percentuale_sconto,
				Data_Inizio=data_inizio,
				Data_Fine=data_fine
			)
			session.add(promozione)
			session.flush()
			return promozione.ID_Promozione

	# ======== VISUALIZZA TUTTI ========
	def get_all_clienti(self):
		with self.db.get_session() as session:
			clienti = session.query(Cliente).all()
			return [
				{
					'ID_Cliente': c.ID_Cliente,
					'Nome': c.Nome,
					'Cognome': c.Cognome,
					'Email': c.Email,
					'Telefono': c.Telefono,
					'Data_Nascita': c.Data_Nascita
				}
				for c in clienti
			]

	def get_all_film(self):
		with self.db.get_session() as session:
			films = session.query(Film).all()
			return [
				{
					'ID_Film': f.ID_Film,
					'Titolo': f.Titolo,
					'Durata': f.Durata,
					'Genere': f.Genere,
					'Classificazione': f.Classificazione,
					'Anno_Uscita': f.Anno_Uscita,
					'ID_Regista': f.ID_Regista
				}
				for f in films
			]

	def get_all_proiezioni(self):
		with self.db.get_session() as session:
			query = """
			SELECT p.ID_Proiezione, f.Titolo, s.Numero AS Sala, p.Data, p.Ora_Inizio, p.Ora_Fine, t.Prezzo_Base
			FROM PROIEZIONE p
			JOIN FILM f ON p.ID_Film = f.ID_Film
			JOIN SALA s ON p.ID_Sala = s.ID_Sala
			JOIN TARIFFA t ON p.ID_Tariffa = t.ID_Tariffa
			ORDER BY p.Data DESC, p.Ora_Inizio
			"""
			result = session.execute(text(query))
			return [dict(row._mapping) for row in result]

	def get_all_sale(self):
		with self.db.get_session() as session:
			sale = session.query(Sala).all()
			return [
				{
					'ID_Sala': s.ID_Sala,
					'Numero': s.Numero,
					'Capienza': s.Capienza,
					'Stato': s.Stato
				}
				for s in sale
			]

	def get_all_operatori(self):
		with self.db.get_session() as session:
			operatori = session.query(Operatore).all()
			return [
				{
					'ID_Operatore': o.ID_Operatore,
					'Nome': o.Nome,
					'Cognome': o.Cognome,
					'Username': o.Username,
					'Ruolo': o.Ruolo
				}
				for o in operatori
			]

	def get_all_tariffe(self):
		with self.db.get_session() as session:
			tariffe = session.query(Tariffa).all()
			return [
				{
					'ID_Tariffa': t.ID_Tariffa,
					'Nome_Tariffa': t.Nome_Tariffa,
					'Prezzo_Base': float(t.Prezzo_Base),
					'Fascia_Oraria': t.Fascia_Oraria,
					'Giorno_Settimana': t.Giorno_Settimana
				}
				for t in tariffe
			]

	def __init__(self):
		self.db = db_manager

	# ========== OPERAZIONI CLIENTE ==========

	def create_cliente(self, nome: str, cognome: str, email: str,
					  telefono: str = None, data_nascita: date = None) -> int:
		with self.db.get_session() as session:
			cliente = Cliente(
				Nome=nome,
				Cognome=cognome,
				Email=email,
				Telefono=telefono,
				Data_Nascita=data_nascita
			)
			session.add(cliente)
			session.flush()
			return cliente.ID_Cliente

	def get_cliente_by_email(self, email: str) -> Optional[Dict]:
		with self.db.get_session() as session:
			cliente = session.query(Cliente).filter(Cliente.Email == email).first()
			if cliente:
				return {
					'ID_Cliente': cliente.ID_Cliente,
					'Nome': cliente.Nome,
					'Cognome': cliente.Cognome,
					'Email': cliente.Email,
					'Telefono': cliente.Telefono,
					'Data_Nascita': cliente.Data_Nascita,
					'Data_Registrazione': cliente.Data_Registrazione
				}
			return None

	def get_cliente_by_id(self, cliente_id: int) -> Optional[Dict]:
		with self.db.get_session() as session:
			cliente = session.query(Cliente).filter(Cliente.ID_Cliente == cliente_id).first()
			if cliente:
				return {
					'ID_Cliente': cliente.ID_Cliente,
					'Nome': cliente.Nome,
					'Cognome': cliente.Cognome,
					'Email': cliente.Email,
					'Telefono': cliente.Telefono,
					'Data_Nascita': cliente.Data_Nascita,
					'Data_Registrazione': cliente.Data_Registrazione
				}
			return None

	def update_cliente(self, cliente_id: int, **kwargs) -> bool:
		with self.db.get_session() as session:
			result = session.query(Cliente).filter(Cliente.ID_Cliente == cliente_id).update(kwargs)
			return result > 0

	def delete_cliente(self, cliente_id: int) -> bool:
		with self.db.get_session() as session:
			cliente = session.query(Cliente).filter(Cliente.ID_Cliente == cliente_id).first()
			if cliente:
				session.delete(cliente)
				return True
			return False

	# ========== OPERAZIONI SALA ==========
	def create_sala(self, numero: int, capienza: int, stato: str) -> int:
		with self.db.get_session() as session:
			sala = Sala(
				Numero=numero,
				Capienza=capienza,
				Stato=stato
			)
			session.add(sala)
			session.flush()
			return sala.ID_Sala

	def create_posto(self, sala_id: int, fila: str, numero_posto: int) -> int:
		with self.db.get_session() as session:
			posto = Posto(
				ID_Sala=sala_id,
				Fila=fila,
				Numero_Posto=numero_posto,
				Stato_Posto='Disponibile'
			)
			session.add(posto)
			session.flush()
			return posto.ID_Posto

	def create_tecnologia(self, nome_tecnologia: str, descrizione: str) -> int:
		with self.db.get_session() as session:
			tecnologia = TipoTecnologia(
				Nome_Tecnologia=nome_tecnologia,
				Descrizione_Tecnologia=descrizione
			)
			session.add(tecnologia)
			session.flush()
			return tecnologia.ID_Tecnologia

	def add_tecnologia_to_sala(self, sala_id: int, tecnologia_id: int) -> int:
		with self.db.get_session() as session:
			supporta = Supporta(
				ID_Sala=sala_id,
				ID_Tecnologia=tecnologia_id
			)
			session.add(supporta)
			session.flush()
			return getattr(supporta, 'ID_Supporta', None)

	def create_tariffa(self, nome_tariffa: str, prezzo_base: float) -> int:
		with self.db.get_session() as session:
			tariffa = Tariffa(
				Nome_Tariffa=nome_tariffa,
				Prezzo_Base=prezzo_base
			)
			session.add(tariffa)
			session.flush()
			return tariffa.ID_Tariffa

	def create_operatore(self, nome: str, cognome: str, ruolo: str) -> int:
		with self.db.get_session() as session:
			operatore = Operatore(
				Nome=nome,
				Cognome=cognome,
				Username=f"{nome.lower()}.{cognome.lower()}",
				Password="password",
				Ruolo=ruolo
			)
			session.add(operatore)
			session.flush()
			return operatore.ID_Operatore

	def create_tipo_promozione(self, nome_tipo: str, descrizione_tipo: str) -> int:
		with self.db.get_session() as session:
			tipo = TipoPromozione(
				Nome_Tipo=nome_tipo,
				Descrizione_Tipo=descrizione_tipo
			)
			session.add(tipo)
			session.flush()
			return tipo.ID_Tipo_Promozione

	# ========== OPERAZIONI FILM ==========

	def create_film(self, titolo: str, durata: int, genere: str,
				   classificazione: str, anno_uscita: int, regista_id: int) -> int:
		with self.db.get_session() as session:
			film = Film(
				Titolo=titolo,
				Durata=durata,
				Genere=genere,
				Classificazione=classificazione,
				Anno_Uscita=anno_uscita,
				ID_Regista=regista_id
			)
			session.add(film)
			session.flush()
			film_id = film.ID_Film
			return film_id

	def get_film_by_genere(self, genere: str) -> List[Dict]:
		with self.db.get_session() as session:
			films = session.query(Film).filter(Film.Genere == genere).all()
			return [
				{
					'ID_Film': f.ID_Film,
					'Titolo': f.Titolo,
					'Durata': f.Durata,
					'Genere': f.Genere,
					'Classificazione': f.Classificazione,
					'Anno_Uscita': f.Anno_Uscita,
					'ID_Regista': f.ID_Regista
				}
				for f in films
			]

	def search_film(self, search_term: str) -> List[Dict]:
		with self.db.get_session() as session:
			films = session.query(Film).filter(
				Film.Titolo.like(f'%{search_term}%')
			).all()
			return [
				{
					'ID_Film': f.ID_Film,
					'Titolo': f.Titolo,
					'Durata': f.Durata,
					'Genere': f.Genere,
					'Classificazione': f.Classificazione,
					'Anno_Uscita': f.Anno_Uscita,
					'ID_Regista': f.ID_Regista
				}
				for f in films
			]

	def delete_film(self, film_id: int) -> bool:
		with self.db.get_session() as session:
			film = session.query(Film).filter(Film.ID_Film == film_id).first()
			if film:
				session.delete(film)
				return True
			return False

	# ========== OPERAZIONI PROIEZIONI ==========

	def create_proiezione(self, data: date, ora_inizio: time, ora_fine: time,
						 film_id: int, sala_id: int, operatore_id: int, tariffa_id: int) -> int:
		with self.db.get_session() as session:
			if self._check_sala_overlap(session, sala_id, data, ora_inizio, ora_fine):
				raise ValueError("Sovrapposizione con altre proiezioni nella stessa sala")

			proiezione = Proiezione(
				Data=data,
				Ora_Inizio=ora_inizio,
				Ora_Fine=ora_fine,
				ID_Film=film_id,
				ID_Sala=sala_id,
				ID_Operatore=operatore_id,
				ID_Tariffa=tariffa_id
			)
			session.add(proiezione)
			session.flush()
			proiezione_id = proiezione.ID_Proiezione
			return proiezione_id

	def get_proiezioni_by_data(self, data: date) -> List[Dict]:
		with self.db.get_session() as session:
			query = """
			SELECT p.ID_Proiezione, f.Titolo, s.Numero AS Sala,
				   p.Ora_Inizio, p.Ora_Fine, t.Prezzo_Base,
				   (s.Capienza - COUNT(b.ID_Biglietto)) AS Posti_Disponibili
			FROM PROIEZIONE p
			JOIN FILM f ON p.ID_Film = f.ID_Film
			JOIN SALA s ON p.ID_Sala = s.ID_Sala
			JOIN TARIFFA t ON p.ID_Tariffa = t.ID_Tariffa
			LEFT JOIN BIGLIETTO b ON p.ID_Proiezione = b.ID_Proiezione AND b.Stato = 'Valido'
			WHERE p.Data = :data
			GROUP BY p.ID_Proiezione
			HAVING Posti_Disponibili > 0
			ORDER BY p.Ora_Inizio
			"""
			result = session.execute(text(query), {'data': data})
			return [dict(row._mapping) for row in result]

	def delete_proiezione(self, proiezione_id: int) -> bool:
		with self.db.get_session() as session:
			proiezione = session.query(Proiezione).filter(Proiezione.ID_Proiezione == proiezione_id).first()
			if proiezione:
				session.delete(proiezione)
				return True
			return False

	def _check_sala_overlap(self, session: Session, sala_id: int, data: date,
						   ora_inizio: time, ora_fine: time, proiezione_id: int = None) -> bool:
		query = session.query(Proiezione).filter(
			and_(
				Proiezione.ID_Sala == sala_id,
				Proiezione.Data == data,
				or_(
					and_(Proiezione.Ora_Inizio <= ora_inizio, Proiezione.Ora_Fine > ora_inizio),
					and_(Proiezione.Ora_Inizio < ora_fine, Proiezione.Ora_Fine >= ora_fine),
					and_(Proiezione.Ora_Inizio >= ora_inizio, Proiezione.Ora_Fine <= ora_fine)
				)
			)
		)

		if proiezione_id:
			query = query.filter(Proiezione.ID_Proiezione != proiezione_id)

		return query.first() is not None

	# ========== OPERAZIONI BIGLIETTI ==========

	def create_biglietto(self, proiezione_id: int, cliente_id: int, posto_id: int,
						promozione_id: int = None) -> Dict:
		with self.db.get_session() as session:
			if self._check_posto_occupied(session, proiezione_id, posto_id):
				raise ValueError("Posto già occupato per questa proiezione")

			prezzo = self._calculate_price(session, proiezione_id, promozione_id)

			biglietto = Biglietto(
				Prezzo_Applicato=prezzo,
				ID_Proiezione=proiezione_id,
				ID_Cliente=cliente_id,
				ID_Posto=posto_id,
				ID_Promozione=promozione_id
			)
			session.add(biglietto)
			session.flush()
			session.refresh(biglietto)

			# Restituisce un dizionario invece dell'oggetto per evitare problemi di sessione
			return {
				'ID_Biglietto': biglietto.ID_Biglietto,
				'Prezzo_Applicato': float(biglietto.Prezzo_Applicato),
				'Stato': biglietto.Stato,
				'Data_Emissione': biglietto.Data_Emissione
			}

	def get_posti_disponibili(self, proiezione_id: int) -> List[Dict]:
		with self.db.get_session() as session:
			query = """
			SELECT po.ID_Posto, po.Numero_Posto, po.Fila
			FROM POSTO po
			WHERE po.ID_Sala = (SELECT ID_Sala FROM PROIEZIONE WHERE ID_Proiezione = :proiezione_id)
			  AND po.Stato_Posto = 'Disponibile'
			  AND po.ID_Posto NOT IN (
				SELECT b.ID_Posto
				FROM BIGLIETTO b
				WHERE b.ID_Proiezione = :proiezione_id AND b.Stato = 'Valido'
			  )
			ORDER BY po.Fila, po.Numero_Posto
			"""
			result = session.execute(text(query), {'proiezione_id': proiezione_id})
			return [dict(row._mapping) for row in result]

	def get_storico_cliente(self, cliente_id: int) -> List[Dict]:
		with self.db.get_session() as session:
			query = """
			SELECT b.ID_Biglietto, f.Titolo, p.Data, p.Ora_Inizio, s.Numero AS Sala,
				   CONCAT(po.Fila, po.Numero_Posto) AS Posto,
				   b.Prezzo_Applicato, b.Stato,
				   pr.Nome AS Promozione
			FROM BIGLIETTO b
			JOIN PROIEZIONE p ON b.ID_Proiezione = p.ID_Proiezione
			JOIN FILM f ON p.ID_Film = f.ID_Film
			JOIN SALA s ON p.ID_Sala = s.ID_Sala
			JOIN POSTO po ON b.ID_Posto = po.ID_Posto
			LEFT JOIN PROMOZIONE pr ON b.ID_Promozione = pr.ID_Promozione
			WHERE b.ID_Cliente = :cliente_id
			ORDER BY p.Data DESC, p.Ora_Inizio DESC
			"""
			result = session.execute(text(query), {'cliente_id': cliente_id})
			return [dict(row._mapping) for row in result]

	def update_biglietto_stato(self, biglietto_id: int, nuovo_stato: str) -> bool:
		with self.db.get_session() as session:
			result = session.query(Biglietto).filter(
				Biglietto.ID_Biglietto == biglietto_id
			).update({'Stato': nuovo_stato})
			return result > 0

	def _check_posto_occupied(self, session: Session, proiezione_id: int, posto_id: int) -> bool:
		return session.query(Biglietto).filter(
			and_(
				Biglietto.ID_Proiezione == proiezione_id,
				Biglietto.ID_Posto == posto_id,
				Biglietto.Stato == 'Valido'
			)
		).first() is not None

	def _calculate_price(self, session: Session, proiezione_id: int, promozione_id: int = None) -> float:
		proiezione = session.query(Proiezione).filter(
			Proiezione.ID_Proiezione == proiezione_id
		).first()

		if not proiezione:
			raise ValueError("Proiezione non trovata")

		prezzo_base = float(proiezione.tariffa.Prezzo_Base)

		if promozione_id:
			promozione = session.query(Promozione).filter(
				and_(
					Promozione.ID_Promozione == promozione_id,
					Promozione.Data_Inizio <= date.today(),
					Promozione.Data_Fine >= date.today()
				)
			).first()

			if promozione:
				sconto = float(promozione.Percentuale_Sconto) / 100
				prezzo_base = prezzo_base * (1 - sconto)

		return round(prezzo_base, 2)

	# ========== OPERAZIONI RECENSIONI ==========

	def create_recensione(self, valutazione: int, commento: str, cliente_id: int, film_id: int) -> int:
		with self.db.get_session() as session:
			existing = session.query(Recensione).filter(
				and_(Recensione.ID_Cliente == cliente_id, Recensione.ID_Film == film_id)
			).first()

			if existing:
				raise ValueError("Recensione già esistente per questo film")

			recensione = Recensione(
				Valutazione=valutazione,
				Commento=commento,
				ID_Cliente=cliente_id,
				ID_Film=film_id
			)
			session.add(recensione)
			session.flush()
			return recensione.ID_Recensione

	def get_recensioni_film(self, film_id: int) -> Dict:
		with self.db.get_session() as session:
			query = """
			SELECT f.Titolo,
				   AVG(r.Valutazione) AS Valutazione_Media,
				   COUNT(r.ID_Recensione) AS Numero_Recensioni,
				   GROUP_CONCAT(
					 CONCAT(c.Nome, ' ', c.Cognome, ': ', r.Valutazione, '/10 - ', r.Commento)
					 SEPARATOR '\n---\n'
				   ) AS Recensioni_Dettagliate
			FROM FILM f
			LEFT JOIN RECENSIONE r ON f.ID_Film = r.ID_Film
			LEFT JOIN CLIENTE c ON r.ID_Cliente = c.ID_Cliente
			WHERE f.ID_Film = :film_id
			GROUP BY f.ID_Film
			"""
			result = session.execute(text(query), {'film_id': film_id})
			row = result.first()
			return dict(row._mapping) if row else {}

	# ========== REPORTS E ANALYTICS ==========

	def get_incassi_giornalieri(self, data_inizio: date, data_fine: date) -> List[Dict]:
		with self.db.get_session() as session:
			query = """
			SELECT DATE(b.Data_Emissione) AS Data,
				   COUNT(b.ID_Biglietto) AS Biglietti_Venduti,
				   SUM(b.Prezzo_Applicato) AS Incasso_Totale,
				   AVG(b.Prezzo_Applicato) AS Prezzo_Medio
			FROM BIGLIETTO b
			WHERE b.Stato IN ('Valido', 'Utilizzato')
			  AND DATE(b.Data_Emissione) BETWEEN :data_inizio AND :data_fine
			GROUP BY DATE(b.Data_Emissione)
			ORDER BY Data DESC
			"""
			result = session.execute(text(query), {
				'data_inizio': data_inizio,
				'data_fine': data_fine
			})
			return [dict(row._mapping) for row in result]

	def get_film_popolari(self, limit: int = 10) -> List[Dict]:
		with self.db.get_session() as session:
			query = """
			SELECT f.Titolo,
				   COUNT(b.ID_Biglietto) AS Biglietti_Venduti,
				   SUM(b.Prezzo_Applicato) AS Incasso,
				   AVG(r.Valutazione) AS Valutazione_Media
			FROM FILM f
			LEFT JOIN PROIEZIONE p ON f.ID_Film = p.ID_Film
			LEFT JOIN BIGLIETTO b ON p.ID_Proiezione = b.ID_Proiezione AND b.Stato != 'Annullato'
			LEFT JOIN RECENSIONE r ON f.ID_Film = r.ID_Film
			GROUP BY f.ID_Film
			ORDER BY Biglietti_Venduti DESC
			LIMIT :limit
			"""
			result = session.execute(text(query), {'limit': limit})
			return [dict(row._mapping) for row in result]

	def create_regista(self, nome: str, cognome: str, nazionalita: str, data_nascita: str) -> int:
		with self.db.get_session() as session:
			regista = Regista(
				Nome_Regista=nome,
				Cognome_Regista=cognome,
				Nazionalita=nazionalita,
				Data_Nascita=data_nascita
			)
			session.add(regista)
			session.flush()
			regista_id = regista.ID_Regista
			return regista_id

	def delete_promozione(self, promozione_id: int) -> bool:
		with self.db.get_session() as session:
			promo = session.query(Promozione).filter(Promozione.ID_Promozione == promozione_id).first()
			if promo:
				session.delete(promo)
				return True
			return False

	def get_all_promozioni(self):
		with self.db.get_session() as session:
			promozioni = session.query(Promozione).all()
			return [
				{
					'ID_Promozione': p.ID_Promozione,
					'Nome': p.Nome,
					'Percentuale_Sconto': float(p.Percentuale_Sconto),
					'Data_Inizio': p.Data_Inizio,
					'Data_Fine': p.Data_Fine
				}
				for p in promozioni
			]

ops = CinemaOperations()
