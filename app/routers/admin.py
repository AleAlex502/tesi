from fastapi import APIRouter, Depends, HTTPException

from app.database import get_connection
from app.auth import get_current_admin, richiedi_amministratore
from app.schemas import MaterialeInput, MaterialeUpdate
from app import crud

router = APIRouter(
    prefix="/admin/materiali",
    tags=["Amministrazione"],
    dependencies=[Depends(get_current_admin)],  # protegge TUTTE le rotte di questo router
)


@router.post("")
def crea_materiale(dati: MaterialeInput):
    """
    Crea un nuovo materiale bibliografico con tutti i collegamenti
    (editore, lingue, persone/ruoli, categoria, tag, subject headings, copie).
    Riservato agli amministratori autenticati.
    """
    connessione = get_connection()
    try:
        id_editore = crud.get_or_create_editore(connessione, dati.editore_nome, dati.editore_citta)
        id_lingua_testo = crud.get_or_create_lingua(connessione, dati.lingua_testo)
        id_lingua_originale = crud.get_or_create_lingua(connessione, dati.lingua_originale)

        cursor = connessione.cursor()
        cursor.execute(
            """
            INSERT INTO Materiale (
                titolo, anno, num_pagine, isbn, abstract, indice,
                tipologia, ebp, livello, link_catalogo,
                id_editore, id_lingua_testo, id_lingua_originale
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                dati.titolo, dati.anno, dati.num_pagine, dati.isbn, dati.abstract, dati.indice,
                dati.tipologia, dati.ebp, dati.livello, dati.link_catalogo,
                id_editore, id_lingua_testo, id_lingua_originale
            )
        )
        connessione.commit()
        id_materiale = cursor.lastrowid
        cursor.close()

        for persona in dati.persone:
            id_persona = crud.get_or_create_persona(connessione, persona.nome_completo)
            crud.collega_materiale_persona(connessione, id_materiale, id_persona, persona.ruolo)

        id_categoria = crud.get_or_create_categoria(connessione, dati.categoria)
        if id_categoria is not None:
            crud.collega_materiale_categoria(connessione, id_materiale, id_categoria)

        for nome_tag in dati.tag:
            id_tag = crud.get_or_create_tag(connessione, nome_tag)
            if id_tag is not None:
                crud.collega_materiale_tag(connessione, id_materiale, id_tag)

        for termine in dati.subject_headings:
            id_sh = crud.get_or_create_sh(connessione, termine)
            if id_sh is not None:
                crud.collega_materiale_sh(connessione, id_materiale, id_sh)

        for copia in dati.copie:
            crud.crea_copia(
                connessione, copia.numero, copia.collocazione,
                copia.stato, copia.note, copia.nota_critica, id_materiale
            )

        return {"id_materiale": id_materiale, "messaggio": "Materiale creato correttamente"}
    finally:
        connessione.close()


@router.put("/{id_materiale}")
def modifica_materiale(id_materiale: int, dati: MaterialeUpdate):
    """
    Modifica solo i campi passati (gli altri restano invariati).
    Non tocca persone/categoria/tag/copie: quelle si gestiscono con
    endpoint dedicati (da aggiungere se vi servirà editarle singolarmente).
    """
    campi_da_aggiornare = dati.model_dump(
        exclude_unset=True,
        exclude={"editore_nome", "editore_citta", "lingua_testo", "lingua_originale"}
    )

    connessione = get_connection()
    try:
        cursor = connessione.cursor()
        cursor.execute("SELECT id_materiale FROM Materiale WHERE id_materiale = %s", (id_materiale,))
        if cursor.fetchone() is None:
            cursor.close()
            raise HTTPException(status_code=404, detail="Materiale non trovato")

        if dati.editore_nome is not None:
            campi_da_aggiornare["id_editore"] = crud.get_or_create_editore(
                connessione, dati.editore_nome, dati.editore_citta
            )

        if dati.lingua_testo is not None:
            campi_da_aggiornare["id_lingua_testo"] = crud.get_or_create_lingua(connessione, dati.lingua_testo)

        if dati.lingua_originale is not None:
            campi_da_aggiornare["id_lingua_originale"] = crud.get_or_create_lingua(connessione, dati.lingua_originale)

        if not campi_da_aggiornare:
            cursor.close()
            return {"messaggio": "Nessun campo da aggiornare"}

        colonne = ", ".join(f"{campo} = %s" for campo in campi_da_aggiornare)
        valori = list(campi_da_aggiornare.values()) + [id_materiale]

        cursor.execute(f"UPDATE Materiale SET {colonne} WHERE id_materiale = %s", valori)
        connessione.commit()
        cursor.close()

        return {"messaggio": "Materiale aggiornato correttamente"}
    finally:
        connessione.close()


@router.delete("/{id_materiale}")
def elimina_materiale(id_materiale: int, admin: dict = Depends(richiedi_amministratore)):
    """
    Elimina un materiale e tutti i suoi collegamenti (copie, associazioni
    con persone/categoria/tag/SH). Le persone, categorie, tag e SH stessi
    NON vengono cancellati, restano riutilizzabili per altri materiali.
    """
    connessione = get_connection()
    try:
        cursor = connessione.cursor()
        cursor.execute("SELECT id_materiale FROM Materiale WHERE id_materiale = %s", (id_materiale,))
        if cursor.fetchone() is None:
            cursor.close()
            raise HTTPException(status_code=404, detail="Materiale non trovato")

        for tabella in ["Copia", "Materiale_Persona", "Materiale_Categoria", "Materiale_Tag", "Materiale_SH"]:
            cursor.execute(f"DELETE FROM {tabella} WHERE id_materiale = %s", (id_materiale,))

        cursor.execute("DELETE FROM Materiale WHERE id_materiale = %s", (id_materiale,))
        connessione.commit()
        cursor.close()

        return {"messaggio": "Materiale eliminato correttamente"}
    finally:
        connessione.close()