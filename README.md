# Catalogo Musicoterapia — Conservatorio di Verona

Web app per la gestione e consultazione del materiale bibliografico di musicoterapia
conservato presso il Conservatorio di Verona. Sostituisce l'archivio precedente in
formato Excel con un sistema digitale strutturato, ricercabile e aggiornabile
direttamente da un'interfaccia web.

## Funzionalità

**Consultazione pubblica** (senza login)
- Ricerca del catalogo per titolo, autore/curatore, anno, editore, lingua, categoria,
  tipologia, tag, livello, stato della copia
- Scheda di dettaglio con dati completi, persone coinvolte, classificazione, copie
  fisiche e allegato PDF (se presente)
- Esportazione dei risultati di ricerca in CSV
- Contatore degli accessi all'archivio

**Pannello di amministrazione** (login richiesto, `/admin`)
- Inserimento, modifica ed eliminazione dei materiali (singola e multipla)
- Caricamento di un allegato PDF per materiale
- Importazione da file Excel, in modalità "aggiungi" (senza duplicati) o
  "sostituisci" (svuota e ricarica l'intero catalogo)
- Due ruoli utente:
  - **Bibliotecario**: può inserire e modificare i materiali
  - **Amministratore**: può inoltre eliminare materiali, importare Excel e creare
    altri account

## Stack tecnico

- **Backend**: Python, FastAPI
- **Database**: MySQL
- **Frontend**: template server-side (Jinja2), nessun framework JS
- **Autenticazione**: JWT (token in cookie per il pannello web, header Bearer per le API)

## Struttura del progetto

```
app/
├── main.py              → avvio dell'app, registrazione dei router
├── config.py             → lettura delle variabili d'ambiente (.env)
├── database.py            → connessione MySQL
├── auth.py                 → hashing password, token JWT, controllo dei permessi
├── crud.py                  → funzioni di accesso al database (create/read/update/delete)
├── schemas.py                → modelli dei dati per l'API JSON
├── routers/
│   ├── materiali.py           → API JSON di consultazione (GET /materiali, /materiali/{id})
│   ├── auth.py                  → API JSON di login (POST /auth/login)
│   ├── admin.py                  → API JSON di amministrazione (POST/PUT/DELETE /admin/materiali)
│   ├── pagine.py                  → pagine HTML pubbliche (ricerca, dettaglio, export CSV)
│   └── admin_pagine.py             → pagine HTML del pannello admin
├── templates/                        → template Jinja2 (HTML)
└── static/                            → CSS e allegati PDF caricati

migrations/                             → script SQL incrementali (da eseguire in ordine numerico)
schema.sql                               → struttura iniziale del database
create_admin.py                           → script per creare il primo account amministratore
import_excel.py                            → script da terminale per importare un file Excel
requirements-backend.txt                    → dipendenze Python
```

## Installazione e avvio in locale

### 1. Prerequisiti
- Python 3.12+
- MySQL Server attivo

### 2. Database

Crea un database vuoto, poi applica la struttura e tutte le migrazioni in ordine:

```bash
mysql -u <utente> -p <nome_db> < schema.sql
mysql -u <utente> -p <nome_db> < migrations/001_amministratore.sql
mysql -u <utente> -p <nome_db> < migrations/002_contatore.sql
mysql -u <utente> -p <nome_db> < migrations/003_ruolo_amministratore.sql
mysql -u <utente> -p <nome_db> < migrations/004_allegato_pdf.sql
```

### 3. Ambiente Python

```bash
python3 -m venv .venv
source .venv/bin/activate          # su Windows: .venv\Scripts\activate
pip install -r requirements-backend.txt
```

### 4. Configurazione

Crea un file `.env` nella cartella principale (vedi `.env.example`):

```
DB_HOST=localhost
DB_USER=<utente>
DB_PASSWORD=<password>
DB_NAME=<nome_db>
JWT_SECRET_KEY=<stringa_casuale_lunga>
```

Genera una `JWT_SECRET_KEY` sicura con:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Primo utente amministratore

```bash
python create_admin.py
```

Segue le indicazioni a schermo (username, password, ruolo → scegli "Amministratore").

### 6. Avvio

```bash
uvicorn app.main:app --reload
```

- Catalogo pubblico: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Pannello admin: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
- Documentazione API interattiva: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 7. (Facoltativo) Importazione dati da Excel

Da terminale:
```bash
python import_excel.py nome_del_file.xlsx
```
oppure dal pannello admin, come Amministratore: **Importa Excel** in alto nella
navigazione. Il file deve avere le stesse colonne del file di esempio incluso nel
repository. Le righe già presenti (stesso ISBN, o stesso numero di copia) non
vengono duplicate.

## Distribuzione online

Il progetto è predisposto per essere ospitato su qualunque servizio che supporti
Python/ASGI (es. Render) con un database MySQL esterno (es. Clever Cloud, Aiven).

- **Build command**: `pip install -r requirements-backend.txt`
- **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Variabili d'ambiente da impostare sulla piattaforma di hosting: le stesse del
  file `.env` (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `JWT_SECRET_KEY`)

**Nota**: gli allegati PDF vengono salvati su disco (`app/static/allegati/`). Su
piattaforme con filesystem effimero (come i piani gratuiti di molti hosting), i
file caricati non sopravvivono a un riavvio o a un nuovo deploy; il database
resta invece sempre intatto.

## Sicurezza

- Le password degli amministratori sono salvate con hashing bcrypt, mai in chiaro
- Il file `.env` non va mai incluso nel repository (verificare che sia elencato in
  `.gitignore`)
- La `JWT_SECRET_KEY` usata in produzione deve essere diversa da quella di sviluppo