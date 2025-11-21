import shell.domain.card_service as card_service
from shell.repl.context import Context
from shell.domain.deck_card import DeckCard
from .base import BaseCommand
import shell.domain.deck_card_service as deck_card_service
import shell.domain.deck_service as deck_service


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
        assert ctx.deck_cards is not None
        try:
            for dc in ctx.deck_cards:
                if dc.card.name == self.card:
                    if dc.is_commander:
                        print("Cannot have more than one commander")
                        return
                    dc.quantidade += self.qty
                    deck_card_service.update_or_insert_deck_card(dc)
                    break
            else:
                card = card_service.get_card_by_name(self.card)
                deck_card = DeckCard(
                    deck_id=ctx.deck.id,
                    card=card,
                    quantidade=self.qty,
                    is_commander=False,
                )
                deck_card_service.update_or_insert_deck_card(deck_card)
                ctx.deck_cards.append(deck_card)
            print(f"Added {self.card} to deck {ctx.deck.name}")
            ctx.deck.update()
            deck_service.save_deck(ctx.deck)
        except Exception as e:
            print(e)
            print("Error adding card to deck")
