from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from app.database import get_connection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dice a FastAPI dove si trova l'endpoint di login (usato solo per generare
# la documentazione /docs, non incide sulla logica).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verifica_password(password_in_chiaro: str, password_hash: str) -> bool:
    return pwd_context.verify(password_in_chiaro, password_hash)


def hash_password(password_in_chiaro: str) -> str:
    return pwd_context.hash(password_in_chiaro)


def crea_access_token(username: str) -> str:
    scadenza = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": scadenza}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_admin_by_username(username: str):
    connessione = get_connection()
    try:
        cursor = connessione.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_admin, username, password_hash, ruolo FROM Amministratore WHERE username = %s",
            (username,)
        )
        admin = cursor.fetchone()
        cursor.close()
        return admin
    finally:
        connessione.close()


def admin_da_token(token: str):
    """
    Come get_current_admin, ma senza sollevare eccezioni: restituisce
    l'admin se il token è valido, altrimenti None. Usata dalle pagine HTML
    (che leggono il token da un cookie invece che dall'header Authorization).
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    return get_admin_by_username(username)


def get_current_admin(token: str = Depends(oauth2_scheme)):
    """
    Dipendenza da usare su tutte le rotte riservate agli admin:
    aggiungendo `admin = Depends(get_current_admin)` ai parametri
    di un endpoint, FastAPI richiede automaticamente un token valido
    e blocca la richiesta con 401 se manca o non è valido.
    """
    eccezione_auth = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide o sessione scaduta",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise eccezione_auth
    except JWTError:
        raise eccezione_auth

    admin = get_admin_by_username(username)
    if admin is None:
        raise eccezione_auth

    return admin


def richiedi_amministratore(admin: dict = Depends(get_current_admin)):
    """
    Dipendenza più restrittiva di get_current_admin: oltre a richiedere un
    login valido, verifica che il ruolo sia "Amministratore" (non basta
    "Bibliotecario"). Usata per eliminare materiali e gestire gli account.
    """
    if admin.get("ruolo") != "Amministratore":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operazione riservata agli amministratori"
        )
    return admin