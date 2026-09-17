# gestisce le connessioni mysql
import mysql.connector
from mysql.connector import Error

from app.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def get_connection():
    """
    Apre una nuova connessione al database.
    Va chiusa esplicitamente dal chiamante 
    """
    try:
        connessione = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connessione
    except Error as err:
        raise RuntimeError(f"Errore di connessione al database: {err}")