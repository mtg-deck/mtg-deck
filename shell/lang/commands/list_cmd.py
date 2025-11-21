from .base import BaseCommand
from shell.repl.context import Context
from shell.domain.deck_service import get_decks
from shell.domain.deck_card_service import get_deck_commanders_name
from tabulate import tabulate


class ListCommand(BaseCommand):
    def __init__(self, qty):
        self.qty = qty

    def run(self, ctx: Context):
        if ctx.deck:
            assert ctx.deck_cards is not None
            try:
                deck_cards = ctx.deck_cards
                data = [["qty", "Card Name", "Commander"]]
                for deck_card in deck_cards:
                    data.append(deck_card.get_list_row())
                print(tabulate(data, headers="firstrow"))
            except Exception as e:
                print("Error getting deck cards")
            return
        try:
            decks = get_decks(limit=self.qty)
        except Exception:
            print("Error getting decks")
            return
        data = [["#", "Name", "Commander", "Last Update"]]
        for deck in decks:
            try:
                commander = get_deck_commanders_name(deck.id)
                data.append([deck.id, deck.name, commander, deck.last_update])
            except Exception as e:
                print(e)
                print(f"Error getting commander for deck {deck.name}")
                return
        print(tabulate(data, headers="firstrow"))
