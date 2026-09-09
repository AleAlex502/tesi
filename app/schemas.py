from typing import List, Optional
from pydantic import BaseModel


class Persona(BaseModel):
    nome_completo: str  # es. "Mario Rossi"
    ruolo: str = "Autore"  # es. "Autore", "Curatore", "Relatore", "Studente"


class Copia(BaseModel):
    numero: str
    collocazione: Optional[str] = None
    stato: Optional[str] = None
    note: Optional[str] = None
    nota_critica: Optional[str] = None


class MaterialeInput(BaseModel):
    titolo: str
    anno: Optional[int] = None
    num_pagine: Optional[int] = None
    isbn: Optional[str] = None
    abstract: Optional[str] = None
    indice: Optional[str] = None
    tipologia: Optional[str] = None  # es. "Libro", "Tesi", "Rivista"
    ebp: Optional[str] = None
    livello: Optional[str] = None
    link_catalogo: Optional[str] = None

    editore_nome: Optional[str] = None
    editore_citta: Optional[str] = None
    lingua_testo: Optional[str] = None
    lingua_originale: Optional[str] = None

    persone: List[Persona] = []
    categoria: Optional[str] = None
    tag: List[str] = []
    subject_headings: List[str] = []
    copie: List[Copia] = []


class MaterialeUpdate(BaseModel):
    """
    Come MaterialeInput ma con tutti i campi opzionali: nella modifica
    l'admin invia solo i campi che vuole effettivamente cambiare.
    """
    titolo: Optional[str] = None
    anno: Optional[int] = None
    num_pagine: Optional[int] = None
    isbn: Optional[str] = None
    abstract: Optional[str] = None
    indice: Optional[str] = None
    tipologia: Optional[str] = None
    ebp: Optional[str] = None
    livello: Optional[str] = None
    link_catalogo: Optional[str] = None
    editore_nome: Optional[str] = None
    editore_citta: Optional[str] = None
    lingua_testo: Optional[str] = None
    lingua_originale: Optional[str] = None