from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <--- 1. Importe isso
from fastapi.staticfiles import StaticFiles
from editor.backend.app.routers.deck import router as deck_router
from editor.backend.app.routers.card import router as card_router
from editor.backend.app.routers.commander import router as commander_router
from infra.config import settings

app = FastAPI(
    title="MTG Commanders App",
    version="0.1.0",
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(card_router)
app.include_router(deck_router)
app.include_router(commander_router)

app.mount(
    "/",
    StaticFiles(directory=settings.BASE_PATH + "/editor/frontend/dist", html=True),
    name="Deck Editor",
)

