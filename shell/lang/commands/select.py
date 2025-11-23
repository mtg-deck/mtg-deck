from .base import BaseCommand
from shell.repl.context import Context
from domain.deck_card_service import get_deck_data_by_name
from commom.excptions import DeckNotFound


class SelectCommand(BaseCommand):
    def __init__(self, deck_name):
        self.deck_name = deck_name

    def run(self, ctx: Context):
        if ctx.deck:
            print("Command not supported on Deck Mode")
            return
        deck, deck_cards = get_deck_data_by_name(self.deck_name)
        ctx.deck = deck
        ctx.deck_cards = deck_cards
        print(f"Deck {self.deck_name} selected")
