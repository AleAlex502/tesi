from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import verifica_password, crea_access_token, get_admin_by_username

router = APIRouter(prefix="/auth", tags=["Autenticazione"])


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login per gli amministratori. Riceve username e password
    (come form, non JSON - è lo standard OAuth2) e restituisce
    un access_token da usare nelle richieste successive, nell'header:
    Authorization: Bearer <token>
    """
    admin = get_admin_by_username(form_data.username)

    if not admin or not verifica_password(form_data.password, admin["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password errati",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = crea_access_token(admin["username"])
    return {"access_token": token, "token_type": "bearer"}