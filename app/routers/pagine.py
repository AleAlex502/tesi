import csv
import io

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.database import get_connection

router = APIRouter(include_in_schema=False)  
templates = Jinja2Templates(directory="app/templates")


def incrementa_e_leggi_contatore(connessione) -> int:
    cursor = connessione.cursor()
    cursor.execute("UPDATE Contatore SET valore = valore + 1 WHERE id = 1")
    connessione.commit()
    cursor.execute("SELECT valore FROM Contatore WHERE id = 1")
    valore = cursor.fetchone()[0]
    cursor.close()
    return valore


def leggi_contatore(connessione) -> int:
    cursor = connessione.cursor()
    cursor.execute("SELECT valore FROM Contatore WHERE id = 1")
    risultato = cursor.fetchone()
    cursor.close()
    return risultato[0] if risultato else 0


def _normalizza_anno(anno: Optional[str]) -> Optional[int]:
    if anno and anno.strip():
        try:
            return int(anno.strip())
        except ValueError:
            return None
    return None


def _costruisci_query_ricerca(titolo, autore, anno_int, editore, lingua, categoria, tipologia, tag, livello, stato):
    """
    Query di ricerca condivisa tra la pagina HTML e l'esportazione CSV,
    così i due restano sempre coerenti sugli stessi filtri.
    """
    condizioni = []
    valori = []

    query = """
        SELECT DISTINCT
            m.id_materiale, m.titolo, m.anno, m.tipologia, m.isbn,
            e.nome AS editore, l.nome AS lingua_testo
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
    if anno_int is not None:
        condizioni.append("m.anno = %s")
        valori.append(anno_int)
    if editore:
        condizioni.append("e.nome LIKE %s")
        valori.append(f"%{editore}%")
    if lingua:
        condizioni.append("l.nome = %s")
        valori.append(lingua)
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

    return query, valori


def _lingue_disponibili(connessione):
    """Le lingue effettivamente presenti nel catalogo, per popolare il menu a tendina"""
    cursor = connessione.cursor()
    cursor.execute("SELECT DISTINCT nome FROM Lingua ORDER BY nome")
    lingue = [riga[0] for riga in cursor.fetchall()]
    cursor.close()
    return lingue


@router.get("/")
def pagina_ricerca(
    request: Request,
    titolo: Optional[str] = None,
    autore: Optional[str] = None,
    anno: Optional[str] = None,
    editore: Optional[str] = None,
    lingua: Optional[str] = None,
    categoria: Optional[str] = None,
    tipologia: Optional[str] = None,
    tag: Optional[str] = None,
    livello: Optional[str] = None,
    stato: Optional[str] = None,
):
    anno_int = _normalizza_anno(anno)
    query, valori = _costruisci_query_ricerca(
        titolo, autore, anno_int, editore, lingua, categoria, tipologia, tag, livello, stato
    )

    connessione = get_connection()
    try:
        contatore = incrementa_e_leggi_contatore(connessione)
        lingue_disponibili = _lingue_disponibili(connessione)

        cursor = connessione.cursor(dictionary=True)
        cursor.execute(query, tuple(valori))
        risultati = cursor.fetchall()
        cursor.close()
    finally:
        connessione.close()

    filtri = {
        "titolo": titolo, "autore": autore, "anno": anno_int,
        "editore": editore, "lingua": lingua, "categoria": categoria, "tipologia": tipologia,
        "tag": tag, "livello": livello, "stato": stato,
    }
    ha_filtri = any(filtri.values())

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "risultati": risultati,
            "filtri": filtri,
            "ha_filtri": ha_filtri,
            "contatore_accessi": contatore,
            "lingue_disponibili": lingue_disponibili,
        }
    )


@router.get("/esporta-csv")
def esporta_csv(
    titolo: Optional[str] = None,
    autore: Optional[str] = None,
    anno: Optional[str] = None,
    editore: Optional[str] = None,
    lingua: Optional[str] = None,
    categoria: Optional[str] = None,
    tipologia: Optional[str] = None,
    tag: Optional[str] = None,
    livello: Optional[str] = None,
    stato: Optional[str] = None,
):
    """
    Esporta in CSV gli stessi risultati che l'utente vede nella pagina di
    ricerca, applicando gli stessi filtri (passati come query string)
    """
    anno_int = _normalizza_anno(anno)
    query, valori = _costruisci_query_ricerca(
        titolo, autore, anno_int, editore, lingua, categoria, tipologia, tag, livello, stato
    )

    connessione = get_connection()
    try:
        cursor = connessione.cursor(dictionary=True)
        cursor.execute(query, tuple(valori))
        risultati = cursor.fetchall()
        cursor.close()
    finally:
        connessione.close()

    buffer = io.StringIO()
    scrittore = csv.writer(buffer, delimiter=";")
    scrittore.writerow(["Titolo", "Anno", "Tipologia", "ISBN", "Editore", "Lingua del testo"])
    for m in risultati:
        isbn = m["isbn"] or ""
        # ="..." forza Excel a trattare l'ISBN come testo, non come numero
        # (altrimenti lo converte in notazione scientifica, es. 9,78E+12)
        isbn_excel = f'="{isbn}"' if isbn else ""
        scrittore.writerow([
            m["titolo"], m["anno"] or "", m["tipologia"] or "",
            isbn_excel, m["editore"] or "", m["lingua_testo"] or "",
        ])

    # Il BOM UTF-8 in testa fa aprire correttamente gli accenti a Excel su Windows.
    contenuto = "\ufeff" + buffer.getvalue()

    return Response(
        content=contenuto,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=catalogo_musicoterapia.csv"}
    )


@router.get("/catalogo/{id_materiale}")
def pagina_dettaglio(request: Request, id_materiale: int):
    connessione = get_connection()
    try:
        contatore = leggi_contatore(connessione)

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
            FROM Materiale_Persona mp JOIN Persona p ON mp.id_persona = p.id_persona
            WHERE mp.id_materiale = %s
            """,
            (id_materiale,)
        )
        materiale["persone"] = cursor.fetchall()

        cursor.execute(
            """
            SELECT c.nome FROM Materiale_Categoria mc JOIN Categoria c ON mc.id_categoria = c.id_categoria
            WHERE mc.id_materiale = %s
            """,
            (id_materiale,)
        )
        materiale["categorie"] = [r["nome"] for r in cursor.fetchall()]

        cursor.execute(
            """
            SELECT t.nome FROM Materiale_Tag mt JOIN Tag t ON mt.id_tag = t.id_tag
            WHERE mt.id_materiale = %s
            """,
            (id_materiale,)
        )
        materiale["tag"] = [r["nome"] for r in cursor.fetchall()]

        cursor.execute(
            """
            SELECT sh.termine FROM Materiale_SH msh JOIN SH sh ON msh.id_sh = sh.id_sh
            WHERE msh.id_materiale = %s
            """,
            (id_materiale,)
        )
        materiale["subject_headings"] = [r["termine"] for r in cursor.fetchall()]

        cursor.execute(
            "SELECT numero, collocazione, stato, note, nota_critica FROM Copia WHERE id_materiale = %s",
            (id_materiale,)
        )
        materiale["copie"] = cursor.fetchall()

        cursor.close()
    finally:
        connessione.close()

    return templates.TemplateResponse(
        "dettaglio.html",
        {"request": request, "materiale": materiale, "contatore_accessi": contatore}
    )