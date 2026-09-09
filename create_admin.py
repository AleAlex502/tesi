"""
Esegui questo script una volta per creare il primo amministratore:

    python create_admin.py

Ti chiederà username e password da terminale (la password non verrà
mostrata mentre la digiti) e la salverà nel database già hashata
(mai in chiaro).
"""
from getpass import getpass

from app.database import get_connection
from app.auth import hash_password


def crea_admin():
    username = input("Username del nuovo amministratore: ").strip()
    password = getpass("Password: ")
    conferma = getpass("Conferma password: ")

    ruolo = input("Ruolo [Bibliotecario/Amministratore] (default: Bibliotecario): ").strip()
    if ruolo not in ("Bibliotecario", "Amministratore"):
        ruolo = "Bibliotecario"

    if password != conferma:
        print("Le due password non coincidono. Riprova.")
        return

    if len(password) < 8:
        print("Attenzione: usa una password di almeno 8 caratteri.")
        return

    connessione = get_connection()
    try:
        cursor = connessione.cursor()
        cursor.execute("SELECT id_admin FROM Amministratore WHERE username = %s", (username,))
        if cursor.fetchone():
            print(f"Esiste già un amministratore con username '{username}'.")
            cursor.close()
            return

        cursor.execute(
            "INSERT INTO Amministratore (username, password_hash, ruolo) VALUES (%s, %s, %s)",
            (username, hash_password(password), ruolo)
        )
        connessione.commit()
        cursor.close()
        print(f"Utente '{username}' creato correttamente con ruolo '{ruolo}'.")
    finally:
        connessione.close()


if __name__ == "__main__":
    crea_admin()