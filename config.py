from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    NAME = "mtg-deck"
    VERSION = "0.1.0"
    DATABASE_URL = "db.sqlite3"
    API_URL = os.getenv("API_URL", "")
    API_KEY = os.getenv("API_KEY", "")
    CLIENT_ID = os.getenv("CLIENT_ID", "")

    def user_is_authenticated(self):
        return self.API_KEY != "" and self.CLIENT_ID != ""


settings = Settings()
