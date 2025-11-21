from .base import BaseCommand
from shell.repl.context import Context
from shell.domain.deck_card_service import get_deck_data_by_name


class SelectCommand(BaseCommand):
    def __init__(self, deck_name):
        self.deck_name = deck_name

    def run(self, ctx: Context):
        if ctx.deck:
            print("Command not supported on Deck Mode")
        try:
            deck, deck_cards = get_deck_data_by_name(self.deck_name)
            if not deck:
                print(f"Deck {self.deck_name} not found")
                return
            ctx.deck = deck
            ctx.deck_cards = deck_cards
            print(f"Deck {self.deck_name} selected")
        except Exception as e:
            print("An error occurred while trying to select deck")
