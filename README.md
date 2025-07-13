## Installazione e Avvio

### 1. Prerequisiti
- **Python 3.8 o superiore**
- **MySQL Server** installato e in esecuzione

Verifica Python:
```bash
python3 --version
```
Verifica MySQL:
```bash
mysql --version
```

### 2. Clona il Repository
```bash
git clone https://github.com/gpeccii/cinema-multisala-db.git
cd cinema-multisala-db
```

### 3. Installa le Dipendenze

#### Mac/Linux
```bash
pip3 install -r requirements.txt
```

#### Windows
```powershell
pip install -r requirements.txt
```

### 4. Configura il Database

Il file `.env` è già fornito nella cartella principale.
Non è necessario modificarlo per il test, a meno che non voglia cambiare utente o password MySQL.

Contenuto di esempio:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=cinema_multisala
DB_USER=root
DB_PASSWORD=
```

### 5. Avvio del Programma

Il database verrà creato automaticamente al primo avvio.

#### Mac/Linux
```bash
python3 main.py
```

#### Windows
```powershell
python main.py
```

---

**Nota:**
Se ricevi errori di connessione, verifica che MySQL sia avviato e che i dati nel `.env` siano ccorretti.
