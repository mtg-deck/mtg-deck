from .base import BaseCommand
from shell.repl.context import Context
from domain.deck_service import get_decks
from domain.deck_card_service import get_deck_commanders_name
from tabulate import tabulate
from commom.deck_list_commands import DeckListCommands
from commom.deck_card_commands import DeckCardCommands


class ListCommand(BaseCommand):
    def __init__(self, qty):
        self.qty = qty

    def run(self, ctx: Context):
        if ctx.deck:
            assert ctx.deck_cards is not None
            assert ctx.deck.name is not None
            cmd = DeckCardCommands.from_deck_name(ctx.deck.name)
            if not cmd:
                return
            cmd.show()
            return
        DeckListCommands.show(self.qty)
