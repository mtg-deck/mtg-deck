from fastapi import FastAPI
from editor.backend.app.routers.deck import router as deck_router
from editor.backend.app.routers.card import router as card_router
from editor.backend.app.routers.commander import router as commander_router
from fastapi.staticfiles import StaticFiles
from infra.config import settings


app = FastAPI(
    title="MTG Commanders App",
    version="0.1.0",
)


app = FastAPI()
app.include_router(card_router)
app.include_router(deck_router)
app.include_router(commander_router)

# app.mount(
#     "/",
#     StaticFiles(directory=settings.BASE_PATH + "/editor/frontend/dist", html=True),
#     name="Deck Editor",
# )
