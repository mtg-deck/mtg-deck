from .base import BaseCommand
import shell.domain.deck_service as deck_service
from shell.repl.context import Context


class CopyCommand(BaseCommand):
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def run(self, ctx: Context):
        if ctx.deck:
            print("Command not supported on Deck Mode")
            return
        try:
            src_deck = deck_service.get_deck_by_name(self.src)
            if not src_deck:
                print(f"Deck {self.src} not found")
                return
            dest_deck = deck_service.get_deck_by_name(self.dest)
            if dest_deck:
                print(f"Deck {self.dest} already exists")
                return
            deck_service.copy_deck(src_deck, self.dest)
            print(f"Deck {self.src} copied to {self.dest}")
        except Exception as e:
            print(e)
            print("An error occurred while trying to copy deck")
