import os
from dotenv import load_dotenv
import pymysql

# Carica variabili da .env
load_dotenv()

def ensure_database_exists():
	try:
		conn = pymysql.connect(
			host=os.getenv("DB_HOST"),
			user=os.getenv("DB_USER"),
			password=os.getenv("DB_PASSWORD"),
			port=int(os.getenv("DB_PORT", 3306)),
			autocommit=True
		)
		with conn.cursor() as cursor:
			cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{os.getenv('DB_NAME')}` DEFAULT CHARACTER SET utf8mb4;")
		conn.close()
	except Exception as e:
		print(f"❌ Errore nella creazione del database: {e}")
		exit(1)

ensure_database_exists()

import os
import sys
from datetime import date, time, datetime, timedelta
from tabulate import tabulate
import logging

from config import AppConfig
from database import init_database, reset_database
from crud_operations import CinemaOperations
from models import *

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CinemaApp:

	def __init__(self):
		self.cinema_ops = CinemaOperations()
		self.current_user = None

	def valida_intero(self, valore, nome_campo, min_valore=None, max_valore=None):
		"""Valida un input numerico intero"""
		try:
			numero = int(valore)
			if min_valore is not None and numero < min_valore:
				print(f"❌ {nome_campo} deve essere maggiore o uguale a {min_valore}!")
				return None
			if max_valore is not None and numero > max_valore:
				print(f"❌ {nome_campo} deve essere minore o uguale a {max_valore}!")
				return None
			return numero
		except ValueError:
			print(f"❌ {nome_campo} deve essere un numero intero!")
			return None

	def valida_float(self, valore, nome_campo, min_valore=None, max_valore=None):
		"""Valida un input numerico decimale"""
		try:
			numero = float(valore)
			if min_valore is not None and numero < min_valore:
				print(f"❌ {nome_campo} deve essere maggiore o uguale a {min_valore}!")
				return None
			if max_valore is not None and numero > max_valore:
				print(f"❌ {nome_campo} deve essere minore o uguale a {max_valore}!")
				return None
			return numero
		except ValueError:
			print(f"❌ {nome_campo} deve essere un numero!")
			return None

	def valida_data(self, valore, nome_campo):
		"""Valida un input di data"""
		try:
			return datetime.strptime(valore, "%Y-%m-%d").date()
		except ValueError:
			print(f"❌ {nome_campo} deve essere nel formato YYYY-MM-DD!")
			return None

	def valida_ora(self, valore, nome_campo):
		"""Valida un input di ora"""
		try:
			return datetime.strptime(valore, "%H:%M").time()
		except ValueError:
			print(f"❌ {nome_campo} deve essere nel formato HH:MM!")
			return None

	def valida_email(self, email):
		"""Validazione base email"""
		if not email or '@' not in email or '.' not in email:
			print("❌ Email non valida! Deve contenere @ e un dominio.")
			return False
		return True

	def valida_telefono(self, telefono):
		"""Validazione base telefono"""
		if telefono and not telefono.replace(' ', '').replace('-', '').replace('+', '').isdigit():
			print("❌ Numero di telefono non valido!")
			return False
		return True

	def valida_stringa_non_vuota(self, valore, nome_campo, lunghezza_min=1, lunghezza_max=None):
		"""Valida una stringa non vuota"""
		if not valore or not valore.strip():
			print(f"❌ {nome_campo} non può essere vuoto!")
			return None

		valore = valore.strip()
		if len(valore) < lunghezza_min:
			print(f"❌ {nome_campo} deve essere di almeno {lunghezza_min} caratteri!")
			return None

		if lunghezza_max and len(valore) > lunghezza_max:
			print(f"❌ {nome_campo} non può superare {lunghezza_max} caratteri!")
			return None

		return valore

	def valida_anno(self, anno):
		"""Valida un anno di uscita film"""
		anno_num = self.valida_intero(anno, "Anno di uscita", 1888, datetime.now().year + 1)
		if anno_num is None:
			return None
		return anno_num

	def valida_durata_film(self, durata):
		"""Valida la durata di un film"""
		return self.valida_intero(durata, "Durata", 1, 600)  # Max 10 ore

	def valida_valutazione(self, valutazione):
		"""Valida una valutazione da 1 a 10"""
		return self.valida_intero(valutazione, "Valutazione", 1, 10)

	def valida_percentuale_sconto(self, percentuale):
		"""Valida una percentuale di sconto"""
		return self.valida_float(percentuale, "Percentuale sconto", 0, 100)

	def mostra_film_disponibili(self):
		"""Mostra tutti i film disponibili in una tabella"""
		film = self.cinema_ops.get_all_film()
		if film:
			headers = ["ID", "Titolo", "Genere", "Durata", "Anno", "Classificazione"]
			rows = []
			for f in film:
				rows.append([
					f['ID_Film'],
					f['Titolo'],
					f['Genere'],
					f"{f['Durata']} min",
					f['Anno_Uscita'],
					f['Classificazione']
				])
			print(f"\n🎬 FILM DISPONIBILI:")
			print(f"{tabulate(rows, headers=headers, tablefmt='grid')}")
			return True
		else:
			print("❌ Nessun film disponibile!")
			return False

	def mostra_proiezioni_disponibili(self):
		"""Mostra tutte le proiezioni disponibili in una tabella"""
		proiezioni = self.cinema_ops.get_all_proiezioni()
		if proiezioni:
			headers = ["ID", "Film", "Sala", "Data", "Ora Inizio", "Ora Fine", "Prezzo"]
			rows = []
			for p in proiezioni:
				rows.append([
					p['ID_Proiezione'],
					p['Titolo'][:25] + "..." if len(p['Titolo']) > 25 else p['Titolo'],
					p['Sala'],
					p['Data'],
					p['Ora_Inizio'],
					p['Ora_Fine'],
					f"€{p['Prezzo_Base']}"
				])
			print(f"\n🎪 PROIEZIONI DISPONIBILI:")
			print(f"{tabulate(rows, headers=headers, tablefmt='grid')}")
			return True
		else:
			print("❌ Nessuna proiezione disponibile!")
			return False

	def mostra_clienti_disponibili(self):
		"""Mostra tutti i clienti disponibili in una tabella"""
		clienti = self.cinema_ops.get_all_clienti()
		if clienti:
			headers = ["ID", "Nome", "Cognome", "Email", "Telefono"]
			rows = []
			for c in clienti:
				rows.append([
					c['ID_Cliente'],
					c['Nome'],
					c['Cognome'],
					c['Email'],
					c['Telefono'] or "-"
				])
			print(f"\n👤 CLIENTI DISPONIBILI:")
			print(f"{tabulate(rows, headers=headers, tablefmt='grid')}")
			return True
		else:
			print("❌ Nessun cliente disponibile!")
			return False

	def mostra_sale_disponibili(self):
		"""Mostra tutte le sale disponibili in una tabella"""
		sale = self.cinema_ops.get_all_sale()
		if sale:
			headers = ["ID", "Numero", "Capienza", "Stato"]
			rows = []
			for s in sale:
				rows.append([
					s['ID_Sala'],
					s['Numero'],
					s['Capienza'],
					s['Stato']
				])
			print(f"\n🎪 SALE DISPONIBILI:")
			print(f"{tabulate(rows, headers=headers, tablefmt='grid')}")
			return True
		else:
			print("❌ Nessuna sala disponibile!")
			return False

	def mostra_operatori_disponibili(self):
		"""Mostra tutti gli operatori disponibili in una tabella"""
		operatori = self.cinema_ops.get_all_operatori()
		if operatori:
			headers = ["ID", "Nome", "Cognome", "Username", "Ruolo"]
			rows = []
			for o in operatori:
				rows.append([
					o['ID_Operatore'],
					o['Nome'],
					o['Cognome'],
					o['Username'],
					o['Ruolo']
				])
			print(f"\n👷 OPERATORI DISPONIBILI:")
			print(f"{tabulate(rows, headers=headers, tablefmt='grid')}")
			return True
		else:
			print("❌ Nessun operatore disponibile!")
			return False

	def mostra_tariffe_disponibili(self):
		"""Mostra tutte le tariffe disponibili in una tabella"""
		tariffe = self.cinema_ops.get_all_tariffe()
		if tariffe:
			headers = ["ID", "Nome", "Prezzo Base", "Fascia Oraria", "Giorno"]
			rows = []
			for t in tariffe:
				rows.append([
					t['ID_Tariffa'],
					t['Nome_Tariffa'],
					f"€{t['Prezzo_Base']}",
					t['Fascia_Oraria'] or "-",
					t['Giorno_Settimana'] or "-"
				])
			print(f"\n💰 TARIFFE DISPONIBILI:")
			print(f"{tabulate(rows, headers=headers, tablefmt='grid')}")
			return True
		else:
			print("❌ Nessuna tariffa disponibile!")
			return False

	def check_database_empty(self):
		"""Verifica se il database è vuoto controllando se esistono film"""
		try:
			films = self.cinema_ops.get_all_film()
			return len(films) == 0
		except Exception as e:
			logger.error(f"Errore nel controllo del database: {e}")
			return True

	def seed_database(self):
		"""Inserisce i dati di mock nel database"""
		try:
			print("🌱 Inserimento dati di esempio...")

			# === REGISTI ===
			regista1_id = self.cinema_ops.create_regista("Federico", "Fellini", "Italiana", "1920-01-20")
			regista2_id = self.cinema_ops.create_regista("Christopher", "Nolan", "Britannica", "1970-07-30")

			# === FILM ===
			film1_id = self.cinema_ops.create_film("La Dolce Vita", 174, "Drammatico", "T", 1960, regista1_id)
			film2_id = self.cinema_ops.create_film("Inception", 148, "Fantascienza", "T", 2010, regista2_id)
			film3_id = self.cinema_ops.create_film("Risate Infinite", 90, "Commedia", "T", 2022, regista2_id)

			# === SALE ===
			sala1_id = self.cinema_ops.create_sala(1, 100, "Attiva")
			sala2_id = self.cinema_ops.create_sala(2, 80, "Attiva")

			# === POSTI ===
			# Sala 1 (100 posti): 10 file da A a J, 10 posti per fila
			for fila in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
				for num in range(1, 11):
					self.cinema_ops.create_posto(sala1_id, fila, num)

			# Sala 2 (80 posti): 8 file da A a H, 10 posti per fila
			for fila in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
				for num in range(1, 11):
					self.cinema_ops.create_posto(sala2_id, fila, num)

			# === TECNOLOGIE ===
			tech1_id = self.cinema_ops.create_tecnologia("2D", "Proiezione standard")
			tech2_id = self.cinema_ops.create_tecnologia("3D", "Proiezione tridimensionale")

			# === SUPPORTA (collega tecnologie alle sale) ===
			self.cinema_ops.add_tecnologia_to_sala(sala1_id, tech1_id)
			self.cinema_ops.add_tecnologia_to_sala(sala1_id, tech2_id)
			self.cinema_ops.add_tecnologia_to_sala(sala2_id, tech1_id)

			# === TARIFFE ===
			tariffa1_id = self.cinema_ops.create_tariffa("Standard", 8.00)
			tariffa2_id = self.cinema_ops.create_tariffa("Weekend", 10.00)

			# === OPERATORI ===
			op1_id = self.cinema_ops.create_operatore("Anna", "Verdi", "Cassiere")
			op2_id = self.cinema_ops.create_operatore("Marco", "Blu", "Proiezionista")

			# === CLIENTI ===
			cliente1_id = self.cinema_ops.create_cliente("Mario", "Rossi", "mario.rossi@email.com", "3331234567", "1990-05-10")
			cliente2_id = self.cinema_ops.create_cliente("Luca", "Bianchi", "luca.bianchi@email.com", "3339876543", "1985-11-22")

			# === PROIEZIONI ===
			oggi = date.today()
			ora_inizio1 = time(18, 0)
			ora_inizio2 = time(20, 30)

			ora_fine1 = time(20, 54)
			ora_fine2 = time(22, 58)

			proiezione1_id = self.cinema_ops.create_proiezione(oggi, ora_inizio1, ora_fine1, film1_id, sala1_id, op2_id, tariffa1_id)
			proiezione2_id = self.cinema_ops.create_proiezione(oggi + timedelta(days=1), ora_inizio2, ora_fine2, film2_id, sala2_id, op2_id, tariffa2_id)

			# === BIGLIETTI ===
			posti_disp1 = self.cinema_ops.get_posti_disponibili(proiezione1_id)
			posti_disp2 = self.cinema_ops.get_posti_disponibili(proiezione2_id)
			if posti_disp1:
				posto1_id = posti_disp1[0]['ID_Posto']
				self.cinema_ops.create_biglietto(proiezione1_id, cliente1_id, posto1_id)
			if posti_disp2:
				posto2_id = posti_disp2[0]['ID_Posto']
				self.cinema_ops.create_biglietto(proiezione2_id, cliente2_id, posto2_id)

			# === TIPI PROMOZIONE E PROMOZIONI ===
			tipo_promo_id = self.cinema_ops.create_tipo_promozione("Sconto Studenti", "Sconto per studenti universitari")
			promo_id = self.cinema_ops.create_promozione("Promo Studenti Luglio", tipo_promo_id, 20, oggi, oggi + timedelta(days=30))

			# === RECENSIONI ===
			self.cinema_ops.create_recensione(9, "Film bellissimo!", cliente1_id, film1_id)
			self.cinema_ops.create_recensione(8, "Molto coinvolgente.", cliente2_id, film2_id)

			print("✅ Dati di esempio inseriti con successo!")

		except Exception as e:
			logger.error(f"Errore nell'inserimento dei dati di esempio: {e}")
			print(f"❌ Errore nell'inserimento dei dati di esempio: {e}")

	def start(self):
		print(f"\n{'='*60}")
		print(f"  {AppConfig.APP_NAME}")
		print(f"  Versione: {AppConfig.APP_VERSION}")
		print(f"  {AppConfig.APP_DESCRIPTION}")
		print(f"{'='*60}\n")

		try:
			init_database()

			# Verifica se il database è vuoto e inserisce i dati di esempio se necessario
			if self.check_database_empty():
				print("📊 Database vuoto rilevato. Inserimento automatico dei dati di esempio...")
				self.seed_database()
				print("🎬 Pronto per l'uso!")
			else:
				print("📊 Database già popolato. Avvio dell'applicazione...")

			self.main_menu()
		except Exception as e:
			logger.error(f"Errore nell'avvio dell'applicazione: {e}")
			print(f"❌ Errore: {e}")

	def main_menu(self):
		while True:
			print("\n🎬 MENU PRINCIPALE")
			print("-" * 30)
			print("1. 👤 Gestione Clienti")
			print("2. 🎭 Gestione Film")
			print("3. 🎪 Gestione Proiezioni")
			print("4. 🎫 Gestione Biglietti")
			print("5. ⭐ Gestione Recensioni")
			print("6. 📊 Reports")
			print("7. ⚙️  Amministrazione")
			print("8. 🚪 Esci")

			choice = input("\nScegli un'opzione (1-8): ").strip()

			if choice == '1':
				self.menu_clienti()
			elif choice == '2':
				self.menu_film()
			elif choice == '3':
				self.menu_proiezioni()
			elif choice == '4':
				self.menu_biglietti()
			elif choice == '5':
				self.menu_recensioni()
			elif choice == '6':
				self.menu_reports()
			elif choice == '7':
				self.menu_admin()
			elif choice == '8':
				print("\n👋 Arrivederci!")
				sys.exit(0)
			else:
				print("❌ Opzione non valida!")

	def menu_clienti(self):
		while True:
			print("\n👤 GESTIONE CLIENTI")
			print("-" * 20)
			print("1. Registra nuovo cliente")
			print("2. Cerca cliente")
			print("3. Aggiorna cliente")
			print("4. Storico acquisti")
			print("5. Visualizza tutti i clienti")
			print("6. Torna al menu principale")

			choice = input("\nScegli un'opzione (1-6): ").strip()

			if choice == '1':
				self.registra_cliente()
			elif choice == '2':
				self.cerca_cliente()
			elif choice == '3':
				self.aggiorna_cliente()
			elif choice == '4':
				self.storico_cliente()
			elif choice == '5':
				self.visualizza_tutti_clienti()
			elif choice == '6':
				break
			else:
				print("❌ Opzione non valida!")

	def visualizza_tutti_clienti(self):
		clienti = self.cinema_ops.get_all_clienti()
		if clienti:
			headers = ["ID", "Nome", "Cognome", "Email", "Telefono", "Data Nascita"]
			rows = []
			for c in clienti:
				rows.append([
					c['ID_Cliente'],
					c['Nome'],
					c['Cognome'],
					c['Email'],
					c['Telefono'] or "-",
					c['Data_Nascita'] or "-"
				])
			print(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}")
		else:
			print("❌ Nessun cliente presente.")

	def registra_cliente(self):
		print("\n📝 REGISTRAZIONE NUOVO CLIENTE")
		print("-" * 35)

		try:
			# Validazione nome
			nome = self.valida_stringa_non_vuota(input("Nome: ").strip(), "Nome", 2, 50)
			if nome is None:
				return

			# Validazione cognome
			cognome = self.valida_stringa_non_vuota(input("Cognome: ").strip(), "Cognome", 2, 50)
			if cognome is None:
				return

			# Validazione email
			email = self.valida_stringa_non_vuota(input("Email: ").strip(), "Email", 5, 100)
			if email is None:
				return

			if not self.valida_email(email):
				return

			# Validazione telefono (opzionale)
			telefono_input = input("Telefono (opzionale): ").strip()
			telefono = None
			if telefono_input:
				if not self.valida_telefono(telefono_input):
					return
				telefono = telefono_input

			# Validazione data di nascita (opzionale)
			data_nascita_str = input("Data di nascita (YYYY-MM-DD, opzionale): ").strip()
			data_nascita = None
			if data_nascita_str:
				data_nascita = self.valida_data(data_nascita_str, "Data di nascita")
				if data_nascita is None:
					return

			cliente_id = self.cinema_ops.create_cliente(nome, cognome, email, telefono, data_nascita)
			print(f"✅ Cliente registrato con successo! ID: {cliente_id}")

		except Exception as e:
			print(f"❌ Errore: {e}")

	def cerca_cliente(self):
		print("\n🔍 RICERCA CLIENTE")
		print("-" * 18)

		email = input("Email del cliente: ").strip()
		cliente = self.cinema_ops.get_cliente_by_email(email)

		if cliente:
			print(f"\n✅ Cliente trovato:")
			print(f"ID: {cliente['ID_Cliente']}")
			print(f"Nome: {cliente['Nome']} {cliente['Cognome']}")
			print(f"Email: {cliente['Email']}")
			print(f"Telefono: {cliente['Telefono'] or 'N/A'}")
			print(f"Data nascita: {cliente['Data_Nascita'] or 'N/A'}")
			print(f"Registrato il: {cliente['Data_Registrazione']}")
		else:
			print("❌ Cliente non trovato!")

	def aggiorna_cliente(self):
		print("\n✏️  AGGIORNA CLIENTE")
		print("-" * 18)

		try:
			cliente_id = self.valida_intero(input("ID Cliente: ").strip(), "ID Cliente", 1)
			if cliente_id is None:
				return

			cliente = self.cinema_ops.get_cliente_by_id(cliente_id)

			if not cliente:
				print("❌ Cliente non trovato!")
				return

			print(f"\nDati attuali: {cliente['Nome']} {cliente['Cognome']} - {cliente['Email']}")

			nome = input(f"Nuovo nome (attuale: {cliente['Nome']}): ").strip() or cliente['Nome']
			cognome = input(f"Nuovo cognome (attuale: {cliente['Cognome']}): ").strip() or cliente['Cognome']
			email = input(f"Nuova email (attuale: {cliente['Email']}): ").strip() or cliente['Email']
			telefono = input(f"Nuovo telefono (attuale: {cliente['Telefono'] or 'N/A'}): ").strip() or cliente['Telefono']

			if self.cinema_ops.update_cliente(cliente_id, Nome=nome, Cognome=cognome, Email=email, Telefono=telefono):
				print("✅ Cliente aggiornato con successo!")
			else:
				print("❌ Errore nell'aggiornamento!")

		except ValueError:
			print("❌ ID non valido!")
		except Exception as e:
			print(f"❌ Errore: {e}")

	def storico_cliente(self):
		print("\n📋 STORICO ACQUISTI")
		print("-" * 20)

		try:
			cliente_id = self.valida_intero(input("ID Cliente: ").strip(), "ID Cliente", 1)
			if cliente_id is None:
				return

			storico = self.cinema_ops.get_storico_cliente(cliente_id)

			if storico:
				headers = ["Biglietto", "Film", "Data", "Ora", "Sala", "Posto", "Prezzo", "Stato", "Promozione"]
				rows = []
				for acquisto in storico:
					rows.append([
						acquisto['ID_Biglietto'],
						acquisto['Titolo'][:30] + "..." if len(acquisto['Titolo']) > 30 else acquisto['Titolo'],
						acquisto['Data'],
						acquisto['Ora_Inizio'],
						acquisto['Sala'],
						acquisto['Posto'],
						f"€{acquisto['Prezzo_Applicato']}",
						acquisto['Stato'],
						acquisto['Promozione'] or "Nessuna"
					])
				print(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}")
			else:
				print("❌ Nessun acquisto trovato per questo cliente!")

		except ValueError:
			print("❌ ID non valido!")
		except Exception as e:
			print(f"❌ Errore: {e}")

	def menu_film(self):
		while True:
			print("\n🎭 GESTIONE FILM")
			print("-" * 16)
			print("1. Aggiungi nuovo film")
			print("2. Cerca film per genere")
			print("3. Ricerca film")
			print("4. Film più popolari")
			print("5. Visualizza tutti i film")
			print("6. Torna al menu principale")

			choice = input("\nScegli un'opzione (1-6): ").strip()

			if choice == '1':
				self.aggiungi_film()
			elif choice == '2':
				self.cerca_film_genere()
			elif choice == '3':
				self.ricerca_film()
			elif choice == '4':
				self.film_popolari()
			elif choice == '5':
				self.visualizza_tutti_film()
			elif choice == '6':
				break
			else:
				print("❌ Opzione non valida!")

		def aggiungi_film(self):
		print("\n🎬 AGGIUNGI NUOVO FILM")
		print("-" * 22)

		try:
			# Input dati del film
			titolo = self.valida_stringa_non_vuota(input("Titolo del film: ").strip(), "Titolo", 1, 100)
			if titolo is None:
				return

			durata = self.valida_durata_film(input("Durata in minuti: ").strip())
			if durata is None:
				return

			genere = self.valida_stringa_non_vuota(input("Genere: ").strip(), "Genere", 2, 50)
			if genere is None:
				return

			classificazione = self.valida_stringa_non_vuota(input("Classificazione (es. T, PG, R): ").strip(), "Classificazione", 1, 10)
			if classificazione is None:
				return

			anno_uscita = self.valida_anno(input("Anno di uscita: ").strip())
			if anno_uscita is None:
				return

			# Input dati del regista
			print("\n📽️  DATI DEL REGISTA")
			print("-" * 18)

			nome_regista = self.valida_stringa_non_vuota(input("Nome regista: ").strip(), "Nome regista", 2, 50)
			if nome_regista is None:
				return

			cognome_regista = self.valida_stringa_non_vuota(input("Cognome regista: ").strip(), "Cognome regista", 2, 50)
			if cognome_regista is None:
				return

			nazionalita = self.valida_stringa_non_vuota(input("Nazionalità: ").strip(), "Nazionalità", 2, 50)
			if nazionalita is None:
				return

			data_nascita_regista_str = input("Data di nascita regista (YYYY-MM-DD, opzionale): ").strip()
			data_nascita_regista = None
			if data_nascita_regista_str:
				data_nascita_regista = self.valida_data(data_nascita_regista_str, "Data di nascita regista")
				if data_nascita_regista is None:
					return

			# Crea il regista
			regista_id = self.cinema_ops.create_regista(
				nome_regista,
				cognome_regista,
				nazionalita,
				data_nascita_regista
			)

			# Crea il film
			film_id = self.cinema_ops.create_film(
				titolo,
				durata,
				genere,
				classificazione,
				anno_uscita,
				regista_id
			)

			print(f"✅ Film aggiunto con successo! ID: {film_id}")
			print(f"📽️  Regista creato con ID: {regista_id}")

		except Exception as e:
			print(f"❌ Errore: {e}")

	def visualizza_tutti_film(self):
		film = self.cinema_ops.get_all_film()
		if film:
			headers = ["ID", "Titolo", "Genere", "Durata", "Anno", "Classificazione"]
			rows = []
			for f in film:
				rows.append([
					f['ID_Film'],
					f['Titolo'],
					f['Genere'],
					f['Durata'],
					f['Anno_Uscita'],
					f['Classificazione']
				])
			print(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}")
		else:
			print("❌ Nessun film presente.")

	def cerca_film_genere(self):
		print("\n🎭 RICERCA PER GENERE")
		print("-" * 23)

		genere = input("Genere: ").strip()
		film = self.cinema_ops.get_film_by_genere(genere)

		if film:
			headers = ["ID", "Titolo", "Durata", "Anno", "Classificazione"]
			rows = []
			for f in film:
				rows.append([f['ID_Film'], f['Titolo'], f"{f['Durata']} min", f['Anno_Uscita'], f['Classificazione']])
			print(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}")
		else:
			print(f"❌ Nessun film trovato per il genere '{genere}'!")

	def ricerca_film(self):
		print("\n🔍 RICERCA FILM")
		print("-" * 15)

		termine = input("Termine di ricerca: ").strip()
		film = self.cinema_ops.search_film(termine)

		if film:
			headers = ["ID", "Titolo", "Genere", "Durata", "Anno"]
			rows = []
			for f in film:
				rows.append([f['ID_Film'], f['Titolo'], f['Genere'], f"{f['Durata']} min", f['Anno_Uscita']])
			print(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}")
		else:
			print(f"❌ Nessun film trovato con '{termine}'!")

	def film_popolari(self):
		print("\n🏆 FILM PIÙ POPOLARI")
		print("-" * 20)

		film = self.cinema_ops.get_film_popolari(10)

		if film:
			headers = ["Titolo", "Biglietti", "Incasso", "Valutazione"]
			rows = []
			for f in film:
				biglietti = f['Biglietti_Venduti'] or 0
				incasso = f"€{f['Incasso'] or 0:.2f}"
				valutazione = f"{f['Valutazione_Media'] or 0:.1f}/10" if f['Valutazione_Media'] else "N/A"
				rows.append([f['Titolo'], biglietti, incasso, valutazione])
			print(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}")
		else:
			print("❌ Nessun dato disponibile!")

	def menu_proiezioni(self):
		while True:
			print("\n🎪 GESTIONE PROIEZIONI")
			print("-" * 22)
			print("1. Proiezioni per data")
			print("2. Aggiungi proiezione")
			print("3. Visualizza tutte le proiezioni")
			print("4. Torna al menu principale")

			choice = input("\nScegli un'opzione (1-4): ").strip()

			if choice == '1':
				self.proiezioni_per_data()
			elif choice == '2':
				self.aggiungi_proiezione()
			elif choice == '3':
				self.visualizza_tutte_proiezioni()
			elif choice == '4':
				break
			else:
				print("❌ Opzione non valida!")

	def visualizza_tutte_proiezioni(self):
		proiezioni = self.cinema_ops.get_all_proiezioni()
		if proiezioni:
			headers = ["ID", "Film", "Sala", "Data", "Ora Inizio", "Ora Fine", "Prezzo"]
			rows = []
			for p in proiezioni:
				rows.append([
					p['ID_Proiezione'],
					p['Titolo'][:25] + "..." if len(p['Titolo']) > 25 else p['Titolo'],
					p['Sala'],
					p['Data'],
					p['Ora_Inizio'],
					p['Ora_Fine'],
					f"€{p['Prezzo_Base']}"
				])
			print(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}")
		else:
			print("❌ Nessuna proiezione presente.")

	def proiezioni_per_data(self):
		print("\n📅 PROIEZIONI PER DATA")
		print("-" * 22)

		try:
			data = self.valida_data(input("Data (YYYY-MM-DD): ").strip(), "Data")
			if data is None:
				return

			proiezioni = self.cinema_ops.get_proiezioni_by_data(data)

			if proiezioni:
				headers = ["ID", "Film", "Sala", "Ora Inizio", "Ora Fine", "Prezzo", "Posti Disp."]
				rows = []
				for p in proiezioni:
					rows.append([
						p['ID_Proiezione'],
						p['Titolo'][:25] + "..." if len(p['Titolo']) > 25 else p['Titolo'],
						p['Sala'],
						p['Ora_Inizio'],
						p['Ora_Fine'],
						f"€{p['Prezzo_Base']}",
						p['Posti_Disponibili']
					])
				print(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}")
			else:
				print(f"❌ Nessuna proiezione trovata per {data}!")

		except ValueError:
			print("❌ Formato data non valido!")
		except Exception as e:
			print(f"❌ Errore: {e}")

	def aggiungi_proiezione(self):
		print("\n➕ AGGIUNGI PROIEZIONE")
		print("-" * 22)

		try:
			# Mostra film disponibili
			if not self.mostra_film_disponibili():
				return

			film_id = int(input("\nID Film: ").strip())

			# Validazione immediata del film
			film = self.cinema_ops.get_all_film()
			film_selezionato = next((f for f in film if f['ID_Film'] == film_id), None)
			if not film_selezionato:
				print("❌ Film non trovato! Verifica l'ID del film.")
				return

			print(f"✅ Film selezionato: {film_selezionato['Titolo']}")

			# Mostra sale disponibili
			if not self.mostra_sale_disponibili():
				return

			sala_id = int(input("\nID Sala: ").strip())

			# Validazione immediata della sala
			sale = self.cinema_ops.get_all_sale()
			sala_selezionata = next((s for s in sale if s['ID_Sala'] == sala_id), None)
			if not sala_selezionata:
				print("❌ Sala non trovata! Verifica l'ID della sala.")
				return

			print(f"✅ Sala selezionata: {sala_selezionata['Numero']} (Capienza: {sala_selezionata['Capienza']})")

			# Mostra operatori disponibili
			if not self.mostra_operatori_disponibili():
				return

			operatore_id = int(input("\nID Operatore: ").strip())

			# Validazione immediata dell'operatore
			operatori = self.cinema_ops.get_all_operatori()
			operatore_selezionato = next((o for o in operatori if o['ID_Operatore'] == operatore_id), None)
			if not operatore_selezionato:
				print("❌ Operatore non trovato! Verifica l'ID dell'operatore.")
				return

			print(f"✅ Operatore selezionato: {operatore_selezionato['Nome']} {operatore_selezionato['Cognome']}")

			# Mostra tariffe disponibili
			if not self.mostra_tariffe_disponibili():
				return

			tariffa_id = int(input("\nID Tariffa: ").strip())

			# Validazione immediata della tariffa
			tariffe = self.cinema_ops.get_all_tariffe()
			tariffa_selezionata = next((t for t in tariffe if t['ID_Tariffa'] == tariffa_id), None)
			if not tariffa_selezionata:
				print("❌ Tariffa non trovata! Verifica l'ID della tariffa.")
				return

			print(f"✅ Tariffa selezionata: {tariffa_selezionata['Nome_Tariffa']} (€{tariffa_selezionata['Prezzo_Base']})")

			# Input data e orari
			data = self.valida_data(input("\nData proiezione (YYYY-MM-DD): ").strip(), "Data proiezione")
			if data is None:
				return

			ora_inizio = self.valida_ora(input("Ora inizio (HH:MM): ").strip(), "Ora inizio")
			if ora_inizio is None:
				return

			# Calcola l'ora di fine basandosi sulla durata del film
			durata_minuti = film_selezionato['Durata']
			ora_inizio_dt = datetime.combine(data, ora_inizio)
			ora_fine_dt = ora_inizio_dt + timedelta(minutes=durata_minuti)
			ora_fine = ora_fine_dt.time()

			print(f"⏰ Ora fine calcolata: {ora_fine.strftime('%H:%M')} (durata film: {durata_minuti} minuti)")

			# Crea la proiezione
			proiezione_id = self.cinema_ops.create_proiezione(data, ora_inizio, ora_fine, film_id, sala_id, operatore_id, tariffa_id)
			print(f"✅ Proiezione creata con successo! ID: {proiezione_id}")

		except ValueError as e:
			print(f"❌ Errore nei dati: {e}")
		except Exception as e:
			print(f"❌ Errore: {e}")

	def menu_biglietti(self):
		while True:
			print("\n🎫 GESTIONE BIGLIETTI")
			print("-" * 21)
			print("1. Vendi biglietto")
			print("2. Posti disponibili")
			print("3. Aggiorna stato biglietto")
			print("4. Torna al menu principale")

			choice = input("\nScegli un'opzione (1-4): ").strip()

			if choice == '1':
				self.vendi_biglietto()
			elif choice == '2':
				self.posti_disponibili()
			elif choice == '3':
				self.aggiorna_biglietto()
			elif choice == '4':
				break
			else:
				print("❌ Opzione non valida!")

	def vendi_biglietto(self):
		print("\n💳 VENDITA BIGLIETTO")
		print("-" * 19)

		try:
			# Mostra proiezioni disponibili
			if not self.mostra_proiezioni_disponibili():
				return

			proiezione_id = int(input("\nID Proiezione: ").strip())

			# Validazione immediata della proiezione
			proiezioni = self.cinema_ops.get_all_proiezioni()
			proiezione_selezionata = next((p for p in proiezioni if p['ID_Proiezione'] == proiezione_id), None)
			if not proiezione_selezionata:
				print("❌ Proiezione non trovata! Verifica l'ID della proiezione.")
				return

			print(f"✅ Proiezione selezionata: {proiezione_selezionata['Titolo']} - Sala {proiezione_selezionata['Sala']}")

			# Mostra clienti disponibili
			if not self.mostra_clienti_disponibili():
				return

			cliente_id = int(input("\nID Cliente: ").strip())

			# Validazione immediata del cliente
			clienti = self.cinema_ops.get_all_clienti()
			cliente_selezionato = next((c for c in clienti if c['ID_Cliente'] == cliente_id), None)
			if not cliente_selezionato:
				print("❌ Cliente non trovato! Verifica l'ID del cliente.")
				return

			print(f"✅ Cliente selezionato: {cliente_selezionato['Nome']} {cliente_selezionato['Cognome']}")

			# Mostra posti disponibili per la proiezione selezionata
			posti = self.cinema_ops.get_posti_disponibili(proiezione_id)
			if posti:
				headers = ["ID Posto", "Fila", "Numero"]
				rows = []
				for posto in posti:
					rows.append([posto['ID_Posto'], posto['Fila'], posto['Numero_Posto']])
				print(f"\n🪑 POSTI DISPONIBILI PER LA PROIEZIONE {proiezione_id}:")
				print(f"{tabulate(rows, headers=headers, tablefmt='grid')}")
			else:
				print("❌ Nessun posto disponibile per questa proiezione!")
				return

			posto_id = int(input("\nID Posto: ").strip())

			# Validazione immediata del posto
			posto_selezionato = next((p for p in posti if p['ID_Posto'] == posto_id), None)
			if not posto_selezionato:
				print("❌ Posto non trovato o non disponibile! Verifica l'ID del posto.")
				return

			print(f"✅ Posto selezionato: {posto_selezionato['Fila']}{posto_selezionato['Numero_Posto']}")

			promozione_input = input("ID Promozione (opzionale): ").strip()
			promozione_id = int(promozione_input) if promozione_input else None

			biglietto_data = self.cinema_ops.create_biglietto(proiezione_id, cliente_id, posto_id, promozione_id)
			print(f"✅ Biglietto venduto! ID: {biglietto_data['ID_Biglietto']}")
			print(f"💰 Prezzo applicato: €{biglietto_data['Prezzo_Applicato']}")

		except ValueError as e:
			print(f"❌ Errore nei dati: {e}")
		except Exception as e:
			print(f"❌ Errore: {e}")

	def posti_disponibili(self):
		print("\n🪑 POSTI DISPONIBILI")
		print("-" * 20)

		try:
			# Mostra proiezioni disponibili
			if not self.mostra_proiezioni_disponibili():
				return

			proiezione_id = self.valida_intero(input("\nID Proiezione: ").strip(), "ID Proiezione", 1)
			if proiezione_id is None:
				return

			posti = self.cinema_ops.get_posti_disponibili(proiezione_id)

			if posti:
				headers = ["ID Posto", "Fila", "Numero"]
				rows = []
				for posto in posti:
					rows.append([posto['ID_Posto'], posto['Fila'], posto['Numero_Posto']])
				print(f"\n🪑 POSTI DISPONIBILI PER LA PROIEZIONE {proiezione_id}:")
				print(f"{tabulate(rows, headers=headers, tablefmt='grid')}")
			else:
				print("❌ Nessun posto disponibile!")

		except ValueError:
			print("❌ ID non valido!")
		except Exception as e:
			print(f"❌ Errore: {e}")

	def aggiorna_biglietto(self):
		print("\n✏️  AGGIORNA BIGLIETTO")
		print("-" * 21)

		try:
			biglietto_id = self.valida_intero(input("ID Biglietto: ").strip(), "ID Biglietto", 1)
			if biglietto_id is None:
				return
			print("\nStati disponibili:")
			print("1. Valido")
			print("2. Utilizzato")
			print("3. Annullato")

			stato_choice = input("Scegli nuovo stato (1-3): ").strip()
			stati = {'1': 'Valido', '2': 'Utilizzato', '3': 'Annullato'}

			if stato_choice in stati:
				nuovo_stato = stati[stato_choice]
				if self.cinema_ops.update_biglietto_stato(biglietto_id, nuovo_stato):
					print(f"✅ Stato aggiornato a: {nuovo_stato}")
				else:
					print("❌ Errore nell'aggiornamento!")
			else:
				print("❌ Stato non valido!")

		except ValueError:
			print("❌ ID non valido!")
		except Exception as e:
			print(f"❌ Errore: {e}")

	def menu_recensioni(self):
		while True:
			print("\n⭐ GESTIONE RECENSIONI")
			print("-" * 22)
			print("1. Aggiungi recensione")
			print("2. Visualizza recensioni film")
			print("3. Torna al menu principale")

			choice = input("\nScegli un'opzione (1-3): ").strip()

			if choice == '1':
				self.aggiungi_recensione()
			elif choice == '2':
				self.visualizza_recensioni()
			elif choice == '3':
				break
			else:
				print("❌ Opzione non valida!")

	def aggiungi_recensione(self):
		print("\n📝 NUOVA RECENSIONE")
		print("-" * 19)

		try:
			# Mostra clienti disponibili
			if not self.mostra_clienti_disponibili():
				return

			cliente_id = int(input("\nID Cliente: ").strip())

			# Validazione immediata del cliente
			clienti = self.cinema_ops.get_all_clienti()
			cliente_selezionato = next((c for c in clienti if c['ID_Cliente'] == cliente_id), None)
			if not cliente_selezionato:
				print("❌ Cliente non trovato! Verifica l'ID del cliente.")
				return

			print(f"✅ Cliente selezionato: {cliente_selezionato['Nome']} {cliente_selezionato['Cognome']}")

			# Mostra film disponibili
			if not self.mostra_film_disponibili():
				return

			film_id = int(input("\nID Film: ").strip())

			# Validazione immediata del film
			film = self.cinema_ops.get_all_film()
			film_selezionato = next((f for f in film if f['ID_Film'] == film_id), None)
			if not film_selezionato:
				print("❌ Film non trovato! Verifica l'ID del film.")
				return

			print(f"✅ Film selezionato: {film_selezionato['Titolo']}")

			valutazione = self.valida_valutazione(input("Valutazione (1-10): ").strip())
			if valutazione is None:
				return

			commento = self.valida_stringa_non_vuota(input("Commento: ").strip(), "Commento", 5, 500)
			if commento is None:
				return

			recensione_id = self.cinema_ops.create_recensione(valutazione, commento, cliente_id, film_id)
			print(f"✅ Recensione aggiunta! ID: {recensione_id}")

		except ValueError as e:
			print(f"❌ Errore nei dati: {e}")
		except Exception as e:
			print(f"❌ Errore: {e}")

	def visualizza_recensioni(self):
		print("\n📊 RECENSIONI FILM")
		print("-" * 17)

		try:
			# Mostra film disponibili
			if not self.mostra_film_disponibili():
				return

			film_id = self.valida_intero(input("\nID Film: ").strip(), "ID Film", 1)
			if film_id is None:
				return

			recensioni = self.cinema_ops.get_recensioni_film(film_id)

			if recensioni and recensioni.get('Numero_Recensioni', 0) > 0:
				print(f"\n🎬 Film: {recensioni['Titolo']}")
				print(f"⭐ Valutazione media: {recensioni['Valutazione_Media']:.1f}/10")
				print(f"📝 Numero recensioni: {recensioni['Numero_Recensioni']}")

				if recensioni.get('Recensioni_Dettagliate'):
					print("\n📋 Recensioni dettagliate:")
					print("-" * 40)
					print(recensioni['Recensioni_Dettagliate'])
			else:
				print("❌ Nessuna recensione trovata per questo film!")

		except ValueError:
			print("❌ ID non valido!")
		except Exception as e:
			print(f"❌ Errore: {e}")

	def menu_reports(self):
		while True:
			print("\n📊 REPORTS")
			print("-" * 10)
			print("1. Incassi giornalieri")
			print("2. Film più popolari")
			print("3. Torna al menu principale")

			choice = input("\nScegli un'opzione (1-3): ").strip()

			if choice == '1':
				self.report_incassi()
			elif choice == '2':
				self.film_popolari()
			elif choice == '3':
				break
			else:
				print("❌ Opzione non valida!")

	def report_incassi(self):
		print("\n💰 INCASSI GIORNALIERI")
		print("-" * 21)

		try:
			data_inizio = self.valida_data(input("Data inizio (YYYY-MM-DD): ").strip(), "Data inizio")
			if data_inizio is None:
				return

			data_fine = self.valida_data(input("Data fine (YYYY-MM-DD): ").strip(), "Data fine")
			if data_fine is None:
				return

			if data_inizio > data_fine:
				print("❌ La data di inizio deve essere precedente alla data di fine!")
				return

			incassi = self.cinema_ops.get_incassi_giornalieri(data_inizio, data_fine)

			if incassi:
				headers = ["Data", "Biglietti", "Incasso", "Prezzo Medio"]
				rows = []
				for i in incassi:
					rows.append([
						i['Data'],
						i['Biglietti_Venduti'],
						f"€{i['Incasso_Totale']:.2f}",
						f"€{i['Prezzo_Medio']:.2f}"
					])
				print(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}")

				# Totali
				totale_biglietti = sum(i['Biglietti_Venduti'] for i in incassi)
				totale_incasso = sum(i['Incasso_Totale'] for i in incassi)
				print(f"\n📈 TOTALI:")
				print(f"🎫 Biglietti venduti: {totale_biglietti}")
				print(f"💰 Incasso totale: €{totale_incasso:.2f}")
			else:
				print("❌ Nessun dato disponibile per il periodo selezionato!")

		except ValueError:
			print("❌ Formato data non valido!")
		except Exception as e:
			print(f"❌ Errore: {e}")

	def menu_admin(self):
		while True:
			print("\n⚙️  AMMINISTRAZIONE")
			print("-" * 17)
			print("1. Reset database")
			print("2. Test connessione")
			print("3. Torna al menu principale")

			choice = input("\nScegli un'opzione (1-3): ").strip()

			if choice == '1':
				self.reset_db()
			elif choice == '2':
				self.test_connessione()
			elif choice == '3':
				break
			else:
				print("❌ Opzione non valida!")

	def reset_db(self):
		print("\n⚠️  RESET DATABASE")
		print("-" * 16)

		conferma = input("ATTENZIONE: Questa operazione cancellerà tutti i dati! Continuare? (si/no): ").strip().lower()

		if conferma == 'si':
			try:
				reset_database()
				print("✅ Database resettato con successo!")
			except Exception as e:
				print(f"❌ Errore nel reset: {e}")
		else:
			print("❌ Operazione annullata!")

	def test_connessione(self):
		print("\n🔗 TEST CONNESSIONE")
		print("-" * 17)

		try:
			self.cinema_ops.db.test_connection()
			print("✅ Connessione al database attiva!")
		except Exception as e:
			print(f"❌ Errore di connessione: {e}")

def main():
	try:
		app = CinemaApp()
		app.start()
	except KeyboardInterrupt:
		print("\n\n👋 Applicazione interrotta dall'utente. Arrivederci!")
	except Exception as e:
		logger.error(f"Errore critico: {e}")
		print(f"\n❌ Errore critico: {e}")

if __name__ == "__main__":
	main()
