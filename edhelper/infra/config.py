from dotenv import load_dotenv
import os
import keyring
from pathlib import Path
import time
from datetime import datetime, date


load_dotenv()

SERVICE_NAME = "edhelper"


class Settings:
    BASE_PATH = Path(__file__).resolve().parents[1]

    NAME = "mtg-deck"
    VERSION = "0.3.0"
    DATABASE_URL = str(BASE_PATH / "db.sqlite3")
    API_URL = "https://mtg-api-production.up.railway.app"

    @property
    def API_KEY(self) -> str:
        keyring_key = keyring.get_password(SERVICE_NAME, "api_key")
        return keyring_key or os.getenv("API_KEY", "")

    @property
    def CLIENT_ID(self) -> str:
        keyring_id = keyring.get_password(SERVICE_NAME, "client_id")
        return keyring_id or os.getenv("CLIENT_ID", "")

    @property
    def SYNC_TIMESTAMP(self) -> str:
        timestamp = keyring.get_password(SERVICE_NAME, "sync_timestamp")
        return timestamp or ""

    @property
    def CARD_SYNC_TIMESTAMP(self) -> str:
        timestamp = keyring.get_password(SERVICE_NAME, "card_sync_timestamp")
        return timestamp or ""

    @property
    def DECK_SYNC_TIMESTAMP(self) -> str:
        timestamp = keyring.get_password(SERVICE_NAME, "deck_sync_timestamp")
        return timestamp or ""

    def can_sync(self):
        timestamp = self.SYNC_TIMESTAMP
        if timestamp == "":
            self.set_sync_timestamp()
            return True
        timestamp_date = datetime.fromtimestamp(float(timestamp))
        today = date.today()
        return today > timestamp_date

    def can_sync_card(self):
        timestamp = self.CARD_SYNC_TIMESTAMP
        if timestamp == "":
            self.set_card_sync_timestamp()
            return True
        MINTIME = 5
        return time.time() - float(timestamp) > MINTIME

    def can_sync_deck(self):
        timestamp = self.DECK_SYNC_TIMESTAMP
        if timestamp == "":
            self.set_deck_sync_timestamp()
            return True
        MINTIME = 60
        return time.time() - float(timestamp) > MINTIME

    def set_sync_timestamp(self):
        timestamp = str(time.time())
        return keyring.set_password(SERVICE_NAME, "sync_timestamp", timestamp)

    def set_card_sync_timestamp(self):
        timestamp = str(time.time())
        return keyring.set_password(SERVICE_NAME, "card_sync_timestamp", timestamp)

    def set_deck_sync_timestamp(self):
        timestamp = str(time.time())
        return keyring.set_password(SERVICE_NAME, "deck_sync_timestamp", timestamp)

    def set_credentials(self, api_key: str, client_id: str):
        keyring.set_password(SERVICE_NAME, "api_key", api_key)
        keyring.set_password(SERVICE_NAME, "client_id", client_id)

    def clear_credentials(self):
        try:
            keyring.delete_password(SERVICE_NAME, "api_key")
        except Exception:
            pass
        try:
            keyring.delete_password(SERVICE_NAME, "client_id")
        except Exception:
            pass

    def user_is_authenticated(self):
        return self.API_KEY != "" and self.CLIENT_ID != ""


settings = Settings()
