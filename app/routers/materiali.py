from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.database import get_connection

router = APIRouter(prefix="/materiali", tags=["Materiali"])


@router.get("")
def cerca_materiali(
    titolo: Optional[str] = Query(None, description="Ricerca parziale nel titolo"),
    autore: Optional[str] = Query(None, description="Nome o cognome di autore/curatore/studente/relatore"),
    anno: Optional[int] = Query(None, description="Anno di pubblicazione"),
    editore: Optional[str] = Query(None, description="Nome dell'editore"),
    lingua: Optional[str] = Query(None, description="Lingua del testo"),
    isbn: Optional[str] = Query(None, description="ISBN esatto"),
    categoria: Optional[str] = Query(None, description="Categoria tematica"),
    tipologia: Optional[str] = Query(None, description="Es. Libro, Tesi, Rivista"),
    tag: Optional[str] = Query(None, description="Tag/parola chiave"),
    livello: Optional[str] = Query(None, description="Livello del materiale"),
    stato: Optional[str] = Query(None, description="Stato di una copia fisica, es. Disponibile"),
):
    """
    Ricerca nel catalogo con filtri opzionali e combinabili.
    Tutti i parametri sono facoltativi: se non passati non filtrano.
    """
    condizioni = []
    valori = []

    query = """
        SELECT DISTINCT
            m.id_materiale,
            m.titolo,
            m.anno,
            m.tipologia,
            m.isbn,
            e.nome AS editore,
            l.nome AS lingua_testo
        FROM Materiale m
        LEFT JOIN Editore e ON m.id_editore = e.id_editore
        LEFT JOIN Lingua l ON m.id_lingua_testo = l.id_lingua
        LEFT JOIN Materiale_Persona mp ON m.id_materiale = mp.id_materiale
        LEFT JOIN Persona p ON mp.id_persona = p.id_persona
        LEFT JOIN Materiale_Categoria mc ON m.id_materiale = mc.id_materiale
        LEFT JOIN Categoria c ON mc.id_categoria = c.id_categoria
        LEFT JOIN Materiale_Tag mt ON m.id_materiale = mt.id_materiale
        LEFT JOIN Tag t ON mt.id_tag = t.id_tag
        LEFT JOIN Copia cp ON m.id_materiale = cp.id_materiale
        WHERE 1=1
    """

    if titolo:
        condizioni.append("m.titolo LIKE %s")
        valori.append(f"%{titolo}%")

    if autore:
        condizioni.append("(p.nome LIKE %s OR p.cognome LIKE %s)")
        valori.extend([f"%{autore}%", f"%{autore}%"])

    if anno:
        condizioni.append("m.anno = %s")
        valori.append(anno)

    if editore:
        condizioni.append("e.nome LIKE %s")
        valori.append(f"%{editore}%")

    if lingua:
        condizioni.append("l.nome LIKE %s")
        valori.append(f"%{lingua}%")

    if isbn:
        condizioni.append("m.isbn = %s")
        valori.append(isbn)

    if categoria:
        condizioni.append("c.nome LIKE %s")
        valori.append(f"%{categoria}%")

    if tipologia:
        condizioni.append("m.tipologia = %s")
        valori.append(tipologia)

    if tag:
        condizioni.append("t.nome LIKE %s")
        valori.append(f"%{tag}%")

    if livello:
        condizioni.append("m.livello LIKE %s")
        valori.append(f"%{livello}%")

    if stato:
        condizioni.append("cp.stato LIKE %s")
        valori.append(f"%{stato}%")

    if condizioni:
        query += " AND " + " AND ".join(condizioni)

    query += " ORDER BY m.titolo"

    connessione = get_connection()
    try:
        cursor = connessione.cursor(dictionary=True)
        cursor.execute(query, tuple(valori))
        risultati = cursor.fetchall()
        cursor.close()
        return risultati
    finally:
        connessione.close()


@router.get("/{id_materiale}")
def dettaglio_materiale(id_materiale: int):
    """
    Restituisce tutti i dettagli di un materiale: dati principali,
    persone coinvolte (con ruolo), categoria, tag, subject headings e copie fisiche.
    """
    connessione = get_connection()
    try:
        cursor = connessione.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                m.*,
                e.nome AS editore_nome, e.citta AS editore_citta,
                lt.nome AS lingua_testo, lo.nome AS lingua_originale
            FROM Materiale m
            LEFT JOIN Editore e ON m.id_editore = e.id_editore
            LEFT JOIN Lingua lt ON m.id_lingua_testo = lt.id_lingua
            LEFT JOIN Lingua lo ON m.id_lingua_originale = lo.id_lingua
            WHERE m.id_materiale = %s
            """,
            (id_materiale,)
        )
        materiale = cursor.fetchone()

        if not materiale:
            cursor.close()
            raise HTTPException(status_code=404, detail="Materiale non trovato")

        cursor.execute(
            """
            SELECT p.nome, p.cognome, mp.ruolo
            FROM Materiale_Persona mp
            JOIN Persona p ON mp.id_persona = p.id_persona
            WHERE mp.id_materiale = %s
            """,
            (id_materiale,)
        )
        materiale["persone"] = cursor.fetchall()

        cursor.execute(
            """
            SELECT c.nome
            FROM Materiale_Categoria mc
            JOIN Categoria c ON mc.id_categoria = c.id_categoria
            WHERE mc.id_materiale = %s
            """,
            (id_materiale,)
        )
        materiale["categorie"] = [r["nome"] for r in cursor.fetchall()]

        cursor.execute(
            """
            SELECT t.nome
            FROM Materiale_Tag mt
            JOIN Tag t ON mt.id_tag = t.id_tag
            WHERE mt.id_materiale = %s
            """,
            (id_materiale,)
        )
        materiale["tag"] = [r["nome"] for r in cursor.fetchall()]

        cursor.execute(
            """
            SELECT sh.termine
            FROM Materiale_SH msh
            JOIN SH sh ON msh.id_sh = sh.id_sh
            WHERE msh.id_materiale = %s
            """,
            (id_materiale,)
        )
        materiale["subject_headings"] = [r["termine"] for r in cursor.fetchall()]

        cursor.execute(
            """
            SELECT numero, collocazione, stato, note, nota_critica
            FROM Copia
            WHERE id_materiale = %s
            """,
            (id_materiale,)
        )
        materiale["copie"] = cursor.fetchall()

        cursor.close()
        return materiale
    finally:
        connessione.close()