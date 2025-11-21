from .base import BaseCommand
import shell.domain.deck_card_service as deck_card_service
import shell.domain.deck_service as deck_service


class RemoveCommand(BaseCommand):
    def __init__(self, card, qty):
        self.card = card.strip()
        self.qty = qty

    def run(self, ctx):
        if ctx.deck is None:
            print("No deck selected")
            return
        assert ctx.deck_cards is not None
        if self.qty <= 0:
            print("Quantity must be greater than 0")
        try:
            for dc in ctx.deck_cards:
                if dc.card.name == self.card:
                    if self.qty > dc.quantidade:
                        self.qty = dc.quantidade
                        deck_card_service.delete_deck_card(dc)
                        ctx.deck_cards.remove(dc)
                        ctx.deck.update()
                        deck_service.save_deck(ctx.deck)
                        break
                    dc.quantidade -= self.qty
                    deck_card_service.update_deck_card_quantity(dc)
                    ctx.deck.update()
                    deck_service.save_deck(ctx.deck)
                    break
            else:
                print(f"Card not found: {self.card}")
                return
            print(f"Removed {self.qty} x {self.card} from deck {ctx.deck.name}")
        except Exception as e:
            print("Error removing card from deck")
