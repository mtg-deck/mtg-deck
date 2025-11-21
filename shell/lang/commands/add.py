from shell.repl.context import Context
from .base import BaseCommand
from commom.deck_card_commands import DeckCardCommands


class AddCommand(BaseCommand):
    def __init__(self, card, qty):
        self.card = card.strip()
        self.qty = qty

    def run(self, ctx: Context):
        if ctx.deck is None:
            print("No deck selected")
            return
        if self.qty <= 0:
            print("Quantity must be greater than 0")
            return
        assert ctx.deck.name is not None
        cmd = DeckCardCommands.from_deck_name(ctx.deck.name)
        if not cmd:
            return
        cmd.add(self.card, self.qty)
        ctx.deck_cards = cmd.deck_cards
