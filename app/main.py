from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import materiali, auth, admin, pagine, admin_pagine

app = FastAPI(
    title="Catalogo Musicoterapia - Conservatorio di Verona",
    description="API per la consultazione e gestione del materiale bibliografico di musicoterapia",
    version="0.1.0"
)

# Permette al frontend i chiamare queste api 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Le pagine HTML per gli utenti 
app.include_router(pagine.router)
app.include_router(admin_pagine.router)
app.include_router(materiali.router)
app.include_router(auth.router)
app.include_router(admin.router)