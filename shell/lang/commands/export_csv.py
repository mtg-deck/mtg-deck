from .base import BaseCommand


class ExportCsvCommand(BaseCommand):
    def __init__(self, deck):
        self.deck = deck

    def run(self, ctx):
        print(f"[export-csv] deck={self.deck}")
