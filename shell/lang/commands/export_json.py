from .base import BaseCommand


class ExportJsonCommand(BaseCommand):
    def __init__(self, deck):
        self.deck = deck

    def run(self, ctx):
        print(f"[export-json] deck={self.deck}")
