# Cinema Multisala Management System

Sistema di gestione per cinema multisala sviluppato per l'E-tivity 4 del corso "Basi di Dati" dell'Università Cusano.

## Studente
**Nome:** Gianmarco Pecci
**Corso:** Basi di Dati - Ingegneria Informatica (L8)
**Anno Accademico:** 2024/2025

## Descrizione del Progetto

Applicazione Python completa per la gestione di un cinema multisala che implementa:
- **Modello E-R** con 13 entità e 14 relazioni
- **Operazioni CRUD** complete con SQLAlchemy ORM
- **Interfaccia console** interattiva
- **Query SQL** ottimizzate per tutte le funzionalità
- **Reports** e analytics

## Tecnologie Utilizzate

- **Python 3.8+**
- **SQLAlchemy 2.0** (ORM)
- **MySQL** (Database)
- **PyMySQL** (Driver MySQL)
- **Tabulate** (Formattazione tabelle)

## Struttura del Progetto

```
cinema_multisala/
├── requirements.txt          # Dipendenze Python
├── config.py                 # Configurazioni database e app
├── models.py                 # Modelli SQLAlchemy (13 entità)
├── database.py               # Gestione connessioni database
├── crud_operations.py        # Operazioni CRUD complete
├── main.py                   # Applicazione principale
├── .env                      # Variabili d'ambiente (opzionale)
└── README.md                 # Questa documentazione
```

## Schema Database

Il sistema implementa **13 entità** e **14 relazioni**:

### Entità Principali
- **REGISTA, FILM, SALA, POSTO**
- **PROIEZIONE, TARIFFA, CLIENTE, OPERATORE**
- **BIGLIETTO, PROMOZIONE, TIPO_PROMOZIONE**
- **TIPO_TECNOLOGIA, RECENSIONE**

### Relazioni
- Relazioni **1:N** per la maggior parte delle associazioni
- Relazione **N:M** tra SALA e TIPO_TECNOLOGIA
- Vincoli di integrità referenziale completi

## Installazione e Setup

### 1. Prerequisiti
```bash
# Python 3.8 o superiore
python --version

# MySQL Server in esecuzione
mysql --version
```

### 2. Clona il Repository
```bash
git clone https://github.com/gpeccii/cinema-multisala-db.git
cd cinema-multisala-db
```

### 3. Installa Dipendenze
```bash
pip install -r requirements.txt
```

### 4. Configura Database
```bash
# Crea database MySQL
mysql -u root -p
CREATE DATABASE cinema_multisala;
EXIT;
```

### 5. Configura Variabili (Opzionale)
Crea file `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=cinema_mult
