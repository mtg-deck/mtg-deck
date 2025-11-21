from .base import BaseCommand
import shell.domain.deck_service as deck_service
from shell.repl.context import Context


class DeleteCommand(BaseCommand):
    def __init__(self, name):
        self.name = name

    def run(self, ctx: Context):
        if ctx.deck:
            print("Command not supported on Deck Mode")
            return
        try:
            deck = deck_service.get_deck_by_name(self.name)
            if not deck:
                print(f"Deck {self.name} not found")
                return
            deck_service.delete_deck(self.name)
            print(f"Deck {self.name} deleted")
        except Exception as e:
            print("An error occurred while trying to delete deck")
