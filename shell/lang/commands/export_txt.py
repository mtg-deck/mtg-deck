from .base import BaseCommand


class ExportTxtCommand(BaseCommand):
    def __init__(self, deck):
        self.deck = deck

    def run(self, ctx):
        print(f"[export-txt] deck={self.deck}")
