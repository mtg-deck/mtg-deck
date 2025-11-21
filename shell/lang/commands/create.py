from .base import BaseCommand
from shell.domain.deck_service import get_deck_by_name, create_deck
from shell.domain.deck import Deck


class CreateCommand(BaseCommand):
    def __init__(self, name):
        self.name = name

    def run(self, ctx):
        if ctx.deck:
            print("Command not supported on Deck Mode")
            return
        try:
            deck = get_deck_by_name(self.name)
        except Exception as e:
            print("An error occurred while trying to create deck")
            print(e)
            return
        if deck:
            print(f"Deck {deck.name} already exists")
            return
        try:
            deck = Deck(name=self.name)
            deck.update()
            create_deck(deck)
            print(f"Deck {deck.name} created")
            return
        except Exception as e:
            print("An error occurred while trying to create deck")
            print(e)
            return
