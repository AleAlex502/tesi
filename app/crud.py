"""
Queste funzioni evitano duplicati cercando prima se la riga esiste già.
Sono condivise dagli endpoint di amministrazione per creare/collegare
editori, lingue, persone, categorie, tag e subject headings.
"""


def get_or_create_editore(connessione, nome, citta):
    if not nome:
        return None

    cursor = connessione.cursor()
    cursor.execute("SELECT id_editore FROM Editore WHERE nome = %s", (nome,))
    risultato = cursor.fetchone()

    if risultato:
        cursor.close()
        return risultato[0]

    cursor.execute("INSERT INTO Editore (nome, citta) VALUES (%s, %s)", (nome, citta))
    connessione.commit()
    id_nuovo = cursor.lastrowid
    cursor.close()
    return id_nuovo


def get_or_create_lingua(connessione, nome):
    if not nome:
        return None

    cursor = connessione.cursor()
    cursor.execute("SELECT id_lingua FROM Lingua WHERE nome = %s", (nome,))
    risultato = cursor.fetchone()

    if risultato:
        cursor.close()
        return risultato[0]

    cursor.execute("INSERT INTO Lingua (nome) VALUES (%s)", (nome,))
    connessione.commit()
    id_nuovo = cursor.lastrowid
    cursor.close()
    return id_nuovo


def get_or_create_persona(connessione, nome_completo):
    cursor = connessione.cursor()

    parti = nome_completo.split()
    if len(parti) == 1:
        nome, cognome = parti[0], ""
    else:
        nome, cognome = " ".join(parti[:-1]), parti[-1]

    cursor.execute(
        "SELECT id_persona FROM Persona WHERE nome = %s AND cognome = %s LIMIT 1",
        (nome, cognome)
    )
    risultato = cursor.fetchone()

    if risultato:
        cursor.close()
        return risultato[0]

    cursor.execute("INSERT INTO Persona (nome, cognome) VALUES (%s, %s)", (nome, cognome))
    connessione.commit()
    id_nuovo = cursor.lastrowid
    cursor.close()
    return id_nuovo


def collega_materiale_persona(connessione, id_materiale, id_persona, ruolo):
    cursor = connessione.cursor()
    cursor.execute(
        "INSERT INTO Materiale_Persona (id_materiale, id_persona, ruolo) VALUES (%s, %s, %s)",
        (id_materiale, id_persona, ruolo)
    )
    connessione.commit()
    cursor.close()


def get_or_create_categoria(connessione, nome):
    if not nome or not nome.strip():
        return None

    cursor = connessione.cursor()
    cursor.execute("SELECT id_categoria FROM Categoria WHERE nome = %s LIMIT 1", (nome,))
    risultato = cursor.fetchone()

    if risultato:
        cursor.close()
        return risultato[0]

    cursor.execute("INSERT INTO Categoria (nome) VALUES (%s)", (nome,))
    connessione.commit()
    id_nuovo = cursor.lastrowid
    cursor.close()
    return id_nuovo


def collega_materiale_categoria(connessione, id_materiale, id_categoria):
    cursor = connessione.cursor()
    cursor.execute(
        "INSERT INTO Materiale_Categoria (id_materiale, id_categoria) VALUES (%s, %s)",
        (id_materiale, id_categoria)
    )
    connessione.commit()
    cursor.close()


def get_or_create_tag(connessione, nome):
    if not nome or not nome.strip():
        return None

    cursor = connessione.cursor()
    cursor.execute("SELECT id_tag FROM Tag WHERE nome = %s LIMIT 1", (nome,))
    risultato = cursor.fetchone()

    if risultato:
        cursor.close()
        return risultato[0]

    cursor.execute("INSERT INTO Tag (nome) VALUES (%s)", (nome,))
    connessione.commit()
    id_nuovo = cursor.lastrowid
    cursor.close()
    return id_nuovo


def collega_materiale_tag(connessione, id_materiale, id_tag):
    cursor = connessione.cursor()
    cursor.execute(
        "INSERT INTO Materiale_Tag (id_materiale, id_tag) VALUES (%s, %s)",
        (id_materiale, id_tag)
    )
    connessione.commit()
    cursor.close()


def get_or_create_sh(connessione, termine):
    if not termine or not termine.strip():
        return None

    cursor = connessione.cursor()
    cursor.execute("SELECT id_sh FROM SH WHERE termine = %s LIMIT 1", (termine,))
    risultato = cursor.fetchone()

    if risultato:
        cursor.close()
        return risultato[0]

    cursor.execute("INSERT INTO SH (termine) VALUES (%s)", (termine,))
    connessione.commit()
    id_nuovo = cursor.lastrowid
    cursor.close()
    return id_nuovo


def collega_materiale_sh(connessione, id_materiale, id_sh):
    cursor = connessione.cursor()
    cursor.execute(
        "INSERT INTO Materiale_SH (id_materiale, id_sh) VALUES (%s, %s)",
        (id_materiale, id_sh)
    )
    connessione.commit()
    cursor.close()


def crea_copia(connessione, numero, collocazione, stato, note, nota_critica, id_materiale):
    cursor = connessione.cursor()
    cursor.execute(
        """
        INSERT INTO Copia (numero, collocazione, stato, note, nota_critica, id_materiale)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (numero, collocazione, stato, note, nota_critica, id_materiale)
    )
    connessione.commit()
    cursor.close()


def elimina_tutti_i_materiali(connessione):
    """
    Cancella tutti i materiali e i loro collegamenti.
    restituisce la lista dei nomi dei file allegato_pdf da cancellare anche dal disco.
    """
    cursor = connessione.cursor()
    cursor.execute("SELECT allegato_pdf FROM Materiale WHERE allegato_pdf IS NOT NULL")
    allegati = [riga[0] for riga in cursor.fetchall()]
    cursor.close()

    cursor = connessione.cursor()
    for tabella in ["Copia", "Materiale_Persona", "Materiale_Categoria", "Materiale_Tag", "Materiale_SH", "Materiale"]:
        cursor.execute(f"DELETE FROM {tabella}")
    connessione.commit()
    cursor.close()

    return allegati


def elimina_materiale(connessione, id_materiale):
    """
    Elimina il materiale e i suoi collegamenti. Restituisce il nome del file
    allegato_pdf che aveva (o None), così il chiamante può cancellarlo anche dal disco.
    """
    cursor = connessione.cursor()
    cursor.execute("SELECT allegato_pdf FROM Materiale WHERE id_materiale = %s", (id_materiale,))
    riga = cursor.fetchone()
    allegato = riga[0] if riga else None
    cursor.close()

    cursor = connessione.cursor()
    for tabella in ["Copia", "Materiale_Persona", "Materiale_Categoria", "Materiale_Tag", "Materiale_SH"]:
        cursor.execute(f"DELETE FROM {tabella} WHERE id_materiale = %s", (id_materiale,))
    cursor.execute("DELETE FROM Materiale WHERE id_materiale = %s", (id_materiale,))
    connessione.commit()
    cursor.close()

    return allegato


def _collega_tutto(connessione, id_materiale, persone, categoria, tag, subject_headings, copie):
    """Collega a un materiale già esistente persone, categoria, tag, SH e copie."""
    for persona in persone:
        id_persona = get_or_create_persona(connessione, persona["nome_completo"])
        collega_materiale_persona(connessione, id_materiale, id_persona, persona.get("ruolo") or "Autore")

    id_categoria = get_or_create_categoria(connessione, categoria)
    if id_categoria is not None:
        collega_materiale_categoria(connessione, id_materiale, id_categoria)

    for nome_tag in tag:
        id_tag = get_or_create_tag(connessione, nome_tag)
        if id_tag is not None:
            collega_materiale_tag(connessione, id_materiale, id_tag)

    for termine in subject_headings:
        id_sh = get_or_create_sh(connessione, termine)
        if id_sh is not None:
            collega_materiale_sh(connessione, id_materiale, id_sh)

    for copia in copie:
        crea_copia(
            connessione, copia["numero"], copia.get("collocazione"),
            copia.get("stato"), copia.get("note"), copia.get("nota_critica"), id_materiale
        )


def crea_materiale_completo(connessione, campi, persone, categoria, tag, subject_headings, copie):
    """
    campi è un dizionario con le colonne dirette di Materiale (titolo, anno, ...)
    più editore_nome/editore_citta/lingua_testo/lingua_originale.
    Usata sia dall'API JSON (POST /admin/materiali) sia dal form HTML admin.
    """
    id_editore = get_or_create_editore(connessione, campi.get("editore_nome"), campi.get("editore_citta"))
    id_lingua_testo = get_or_create_lingua(connessione, campi.get("lingua_testo"))
    id_lingua_originale = get_or_create_lingua(connessione, campi.get("lingua_originale"))

    cursor = connessione.cursor()
    cursor.execute(
        """
        INSERT INTO Materiale (
            titolo, anno, num_pagine, isbn, abstract, indice,
            tipologia, ebp, livello, link_catalogo, allegato_pdf,
            id_editore, id_lingua_testo, id_lingua_originale
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            campi.get("titolo"), campi.get("anno"), campi.get("num_pagine"), campi.get("isbn"),
            campi.get("abstract"), campi.get("indice"), campi.get("tipologia"), campi.get("ebp"),
            campi.get("livello"), campi.get("link_catalogo"), campi.get("allegato_pdf"),
            id_editore, id_lingua_testo, id_lingua_originale
        )
    )
    connessione.commit()
    id_materiale = cursor.lastrowid
    cursor.close()

    _collega_tutto(connessione, id_materiale, persone, categoria, tag, subject_headings, copie)

    return id_materiale


def aggiorna_materiale_completo(connessione, id_materiale, campi, persone, categoria, tag, subject_headings, copie):
    """
    Aggiorna i campi diretti del materiale e sostituisce interamente i suoi
    collegamenti (persone, categoria, tag, SH, copie) con quelli passati
    """
    id_editore = get_or_create_editore(connessione, campi.get("editore_nome"), campi.get("editore_citta"))
    id_lingua_testo = get_or_create_lingua(connessione, campi.get("lingua_testo"))
    id_lingua_originale = get_or_create_lingua(connessione, campi.get("lingua_originale"))

    cursor = connessione.cursor()
    cursor.execute(
        """
        UPDATE Materiale SET
            titolo = %s, anno = %s, num_pagine = %s, isbn = %s, abstract = %s, indice = %s,
            tipologia = %s, ebp = %s, livello = %s, link_catalogo = %s, allegato_pdf = %s,
            id_editore = %s, id_lingua_testo = %s, id_lingua_originale = %s
        WHERE id_materiale = %s
        """,
        (
            campi.get("titolo"), campi.get("anno"), campi.get("num_pagine"), campi.get("isbn"),
            campi.get("abstract"), campi.get("indice"), campi.get("tipologia"), campi.get("ebp"),
            campi.get("livello"), campi.get("link_catalogo"), campi.get("allegato_pdf"),
            id_editore, id_lingua_testo, id_lingua_originale,
            id_materiale
        )
    )
    connessione.commit()
    cursor.close()

    cursor = connessione.cursor()
    for tabella in ["Materiale_Persona", "Materiale_Categoria", "Materiale_Tag", "Materiale_SH", "Copia"]:
        cursor.execute(f"DELETE FROM {tabella} WHERE id_materiale = %s", (id_materiale,))
    connessione.commit()
    cursor.close()

    _collega_tutto(connessione, id_materiale, persone, categoria, tag, subject_headings, copie)


# ---------- Parsing dei campi testuali inviati dal form HTML admin ----------

def parse_persone_testo(testo):
    """
    Una persona per riga, stesso formato usato in import_excel.py:
    "Mario Rossi" oppure "Mario Rossi (Curatore)".
    """
    risultato = []
    if not testo:
        return risultato

    for riga in testo.splitlines():
        riga = riga.strip()
        if not riga:
            continue

        if "(" in riga and riga.endswith(")"):
            nome_completo, ruolo = riga.rsplit("(", 1)
            nome_completo = nome_completo.strip()
            ruolo = ruolo[:-1].strip()
        else:
            nome_completo = riga
            ruolo = "Autore"

        risultato.append({"nome_completo": nome_completo, "ruolo": ruolo})

    return risultato


def parse_lista_semplice(testo):
    """Valori separati da virgola, per tag e subject headings."""
    if not testo:
        return []
    return [voce.strip() for voce in testo.split(",") if voce.strip()]


def parse_copie_testo(testo):
    """Una copia per riga, formato: numero;collocazione;stato;note"""
    risultato = []
    if not testo:
        return risultato

    for riga in testo.splitlines():
        riga = riga.strip()
        if not riga:
            continue

        parti = [p.strip() for p in riga.split(";")]
        numero = parti[0] if len(parti) > 0 else ""
        if not numero:
            continue

        risultato.append({
            "numero": numero,
            "collocazione": parti[1] if len(parti) > 1 and parti[1] else None,
            "stato": parti[2] if len(parti) > 2 and parti[2] else None,
            "note": parti[3] if len(parti) > 3 and parti[3] else None,
            "nota_critica": None,
        })

    return risultato


# ---------- Importazione da Excel  ----------
# eviano duplicati

def get_or_create_materiale(
    connessione, titolo, anno, num_pagine, isbn, abstract, indice,
    tipologia, ebp, livello, link_catalogo, id_editore, id_lingua_testo, id_lingua_originale
):
    cursor = connessione.cursor()

    if isbn:
        cursor.execute("SELECT id_materiale FROM Materiale WHERE isbn = %s LIMIT 1", (isbn,))
    else:
        cursor.execute(
            "SELECT id_materiale FROM Materiale WHERE titolo = %s AND anno = %s AND tipologia = %s LIMIT 1",
            (titolo, anno, tipologia)
        )

    risultato = cursor.fetchone()
    if risultato:
        cursor.close()
        return risultato[0]

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
            titolo, anno, num_pagine, isbn, abstract, indice,
            tipologia, ebp, livello, link_catalogo,
            id_editore, id_lingua_testo, id_lingua_originale
        )
    )
    connessione.commit()
    id_materiale = cursor.lastrowid
    cursor.close()
    return id_materiale


def get_or_create_copia_excel(connessione, numero, collocazione, stato, note, nota_critica, id_materiale):
    cursor = connessione.cursor()
    cursor.execute("SELECT id_copia FROM Copia WHERE numero = %s", (numero,))
    risultato = cursor.fetchone()

    if risultato:
        cursor.close()
        return risultato[0]

    cursor.execute(
        "INSERT INTO Copia (numero, collocazione, stato, note, nota_critica, id_materiale) VALUES (%s, %s, %s, %s, %s, %s)",
        (numero, collocazione, stato, note, nota_critica, id_materiale)
    )
    connessione.commit()
    id_copia = cursor.lastrowid
    cursor.close()
    return id_copia


def _collega_dedup(connessione, tabella, colonne, valori):
    cursor = connessione.cursor()
    condizione = " AND ".join(f"{c} = %s" for c in colonne)
    cursor.execute(f"SELECT * FROM {tabella} WHERE {condizione} LIMIT 1", valori)
    if not cursor.fetchone():
        segnaposto = ", ".join(["%s"] * len(colonne))
        cursor.execute(
            f"INSERT INTO {tabella} ({', '.join(colonne)}) VALUES ({segnaposto})", valori
        )
        connessione.commit()
    cursor.close()


def importa_riga_excel(connessione, row):
    """
    Importa una riga del file Excel evitando duplicati. 
    Restituisce l'id_materiale (nuovo o già esistente).
    """
    testo_persone = row.get("Autore / Curatore") or ""
    lista_persone = testo_persone.split(";")

    id_editore = get_or_create_editore(connessione, row.get("Editore"), row.get("Città editore"))
    id_lingua_testo = get_or_create_lingua(connessione, row.get("Lingua testo"))
    id_lingua_originale = get_or_create_lingua(connessione, row.get("Lingua originale"))

    id_materiale = get_or_create_materiale(
        connessione,
        row.get("Titolo"), row.get("Anno"), row.get("N. pagine"), row.get("ISBN"),
        row.get("Abstract"), row.get("Indice"), row.get("Tipologia"), row.get("EBP"),
        row.get("Livello"), row.get("Link catalogo ABV"),
        id_editore, id_lingua_testo, id_lingua_originale
    )

    id_categoria = get_or_create_categoria(connessione, row.get("Categoria"))
    if id_categoria is not None:
        _collega_dedup(connessione, "Materiale_Categoria", ["id_materiale", "id_categoria"], (id_materiale, id_categoria))

    for colonna in ["Tag 1", "Tag 2", "Tag 3", "Tag 4"]:
        id_tag = get_or_create_tag(connessione, row.get(colonna))
        if id_tag is not None:
            _collega_dedup(connessione, "Materiale_Tag", ["id_materiale", "id_tag"], (id_materiale, id_tag))

    for colonna in ["SH 1", "SH 2", "SH 3"]:
        id_sh = get_or_create_sh(connessione, row.get(colonna))
        if id_sh is not None:
            _collega_dedup(connessione, "Materiale_SH", ["id_materiale", "id_sh"], (id_materiale, id_sh))

    get_or_create_copia_excel(
        connessione, row.get("N."), row.get("Collocazione"), row.get("Stato"),
        row.get("Note"), row.get("Nota critica"), id_materiale
    )

    for persona in lista_persone:
        persona = persona.strip()
        if not persona:
            continue

        if "(" in persona and persona.endswith(")"):
            nome_completo, ruolo = persona.rsplit("(", 1)
            nome_completo = nome_completo.strip()
            ruolo = ruolo[:-1].strip()
        else:
            nome_completo = persona
            ruolo = "Autore"

        id_persona = get_or_create_persona(connessione, nome_completo)
        _collega_dedup(connessione, "Materiale_Persona", ["id_materiale", "id_persona", "ruolo"], (id_materiale, id_persona, ruolo))

    return id_materiale