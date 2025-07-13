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
from datetime import date, time, datetime
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

    def start(self):
        print(f"\n{'='*60}")
        print(f"  {AppConfig.APP_NAME}")
        print(f"  Versione: {AppConfig.APP_VERSION}")
        print(f"  {AppConfig.APP_DESCRIPTION}")
        print(f"{'='*60}\n")

        try:
            init_database()
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
            print("5. Torna al menu principale")

            choice = input("\nScegli un'opzione (1-5): ").strip()

            if choice == '1':
                self.registra_cliente()
            elif choice == '2':
                self.cerca_cliente()
            elif choice == '3':
                self.aggiorna_cliente()
            elif choice == '4':
                self.storico_cliente()
            elif choice == '5':
                break
            else:
                print("❌ Opzione non valida!")

    def registra_cliente(self):
        print("\n📝 REGISTRAZIONE NUOVO CLIENTE")
        print("-" * 35)

        try:
            nome = input("Nome: ").strip()
            cognome = input("Cognome: ").strip()
            email = input("Email: ").strip()
            telefono = input("Telefono (opzionale): ").strip() or None

            data_nascita_str = input("Data di nascita (YYYY-MM-DD, opzionale): ").strip()
            data_nascita = None
            if data_nascita_str:
                data_nascita = datetime.strptime(data_nascita_str, "%Y-%m-%d").date()

            cliente = self.cinema_ops.create_cliente(nome, cognome, email, telefono, data_nascita)
            print(f"✅ Cliente registrato con successo! ID: {cliente.ID_Cliente}")

        except ValueError as e:
            print(f"❌ Errore nei dati: {e}")
        except Exception as e:
            print(f"❌ Errore: {e}")

    def cerca_cliente(self):
        print("\n🔍 RICERCA CLIENTE")
        print("-" * 18)

        email = input("Email del cliente: ").strip()
        cliente = self.cinema_ops.get_cliente_by_email(email)

        if cliente:
            print(f"\n✅ Cliente trovato:")
            print(f"ID: {cliente.ID_Cliente}")
            print(f"Nome: {cliente.Nome} {cliente.Cognome}")
            print(f"Email: {cliente.Email}")
            print(f"Telefono: {cliente.Telefono or 'N/A'}")
            print(f"Data nascita: {cliente.Data_Nascita or 'N/A'}")
            print(f"Registrato il: {cliente.Data_Registrazione}")
        else:
            print("❌ Cliente non trovato!")

    def aggiorna_cliente(self):
        print("\n✏️  AGGIORNA CLIENTE")
        print("-" * 18)

        try:
            cliente_id = int(input("ID Cliente: ").strip())
            cliente = self.cinema_ops.get_cliente_by_id(cliente_id)

            if not cliente:
                print("❌ Cliente non trovato!")
                return

            print(f"\nDati attuali: {cliente.Nome} {cliente.Cognome} - {cliente.Email}")

            nome = input(f"Nuovo nome (attuale: {cliente.Nome}): ").strip() or cliente.Nome
            cognome = input(f"Nuovo cognome (attuale: {cliente.Cognome}): ").strip() or cliente.Cognome
            email = input(f"Nuova email (attuale: {cliente.Email}): ").strip() or cliente.Email
            telefono = input(f"Nuovo telefono (attuale: {cliente.Telefono or 'N/A'}): ").strip() or cliente.Telefono

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
            cliente_id = int(input("ID Cliente: ").strip())
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
            print("1. Cerca film per genere")
            print("2. Ricerca film")
            print("3. Film più popolari")
            print("4. Torna al menu principale")

            choice = input("\nScegli un'opzione (1-4): ").strip()

            if choice == '1':
                self.cerca_film_genere()
            elif choice == '2':
                self.ricerca_film()
            elif choice == '3':
                self.film_popolari()
            elif choice == '4':
                break
            else:
                print("❌ Opzione non valida!")

    def cerca_film_genere(self):
        print("\n🎭 RICERCA PER GENERE")
        print("-" * 23)

        genere = input("Genere: ").strip()
        film = self.cinema_ops.get_film_by_genere(genere)

        if film:
            headers = ["ID", "Titolo", "Durata", "Anno", "Classificazione"]
            rows = []
            for f in film:
                rows.append([f.ID_Film, f.Titolo, f"{f.Durata} min", f.Anno_Uscita, f.Classificazione])
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
                rows.append([f.ID_Film, f.Titolo, f.Genere, f"{f.Durata} min", f.Anno_Uscita])
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
            print("3. Torna al menu principale")

            choice = input("\nScegli un'opzione (1-3): ").strip()

            if choice == '1':
                self.proiezioni_per_data()
            elif choice == '2':
                self.aggiungi_proiezione()
            elif choice == '3':
                break
            else:
                print("❌ Opzione non valida!")

    def proiezioni_per_data(self):
        print("\n📅 PROIEZIONI PER DATA")
        print("-" * 22)

        try:
            data_str = input("Data (YYYY-MM-DD): ").strip()
            data = datetime.strptime(data_str, "%Y-%m-%d").date()

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
        print("⚠️  Funzione disponibile solo per amministratori")

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
            proiezione_id = int(input("ID Proiezione: ").strip())
            cliente_id = int(input("ID Cliente: ").strip())
            posto_id = int(input("ID Posto: ").strip())

            promozione_input = input("ID Promozione (opzionale): ").strip()
            promozione_id = int(promozione_input) if promozione_input else None

            biglietto = self.cinema_ops.create_biglietto(proiezione_id, cliente_id, posto_id, promozione_id)
            print(f"✅ Biglietto venduto! ID: {biglietto.ID_Biglietto}")
            print(f"💰 Prezzo applicato: €{biglietto.Prezzo_Applicato}")

        except ValueError as e:
            print(f"❌ Errore nei dati: {e}")
        except Exception as e:
            print(f"❌ Errore: {e}")

    def posti_disponibili(self):
        print("\n🪑 POSTI DISPONIBILI")
        print("-" * 20)

        try:
            proiezione_id = int(input("ID Proiezione: ").strip())
            posti = self.cinema_ops.get_posti_disponibili(proiezione_id)

            if posti:
                headers = ["ID Posto", "Fila", "Numero"]
                rows = []
                for posto in posti:
                    rows.append([posto['ID_Posto'], posto['Fila'], posto['Numero_Posto']])
                print(f"\n{tabulate(rows, headers=headers, tablefmt='grid')}")
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
            biglietto_id = int(input("ID Biglietto: ").strip())
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
            cliente_id = int(input("ID Cliente: ").strip())
            film_id = int(input("ID Film: ").strip())
            valutazione = int(input("Valutazione (1-10): ").strip())

            if not (1 <= valutazione <= 10):
                print("❌ Valutazione deve essere tra 1 e 10!")
                return

            commento = input("Commento: ").strip()

            recensione = self.cinema_ops.create_recensione(valutazione, commento, cliente_id, film_id)
            print(f"✅ Recensione aggiunta! ID: {recensione.ID_Recensione}")

        except ValueError as e:
            print(f"❌ Errore nei dati: {e}")
        except Exception as e:
            print(f"❌ Errore: {e}")

    def visualizza_recensioni(self):
        print("\n📊 RECENSIONI FILM")
        print("-" * 17)

        try:
            film_id = int(input("ID Film: ").strip())
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
            data_inizio_str = input("Data inizio (YYYY-MM-DD): ").strip()
            data_fine_str = input("Data fine (YYYY-MM-DD): ").strip()

            data_inizio = datetime.strptime(data_inizio_str, "%Y-%m-%d").date()
            data_fine = datetime.strptime(data_fine_str, "%Y-%m-%d").date()

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
