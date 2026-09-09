# Sistema di catalogazione del materiale bibliografico di Musicoterapia

## Descrizione

Il progetto realizza il database per la catalogazione del materiale bibliografico del Conservatorio di Verona.

È stato sviluppato utilizzando MySQL e Python. Lo script `import_excel.py` importa automaticamente i dati presenti nel file Excel nel database, evitando duplicati e gestendo le relazioni tra materiali, copie, persone, categorie, tag e Subject Headings (SH).

## Contenuto del progetto

- `schema.dbml` – modello del database.
- `schema.sql` – script di creazione del database.
- `import_excel.py` – script di importazione dei dati.
- `Excel_test_catalogazione_musicoterapia.xlsx` – file Excel di esempio.