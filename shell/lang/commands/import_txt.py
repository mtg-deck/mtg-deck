from .base import BaseCommand
from shell.lang.validators import validate_txt
import shell.domain.deck_service as deck_service
import shell.domain.card_service as card_service
from shell.repl.context import Context


class ImportTxtCommand(BaseCommand):
    def __init__(self, filename, deck_name):
        self.filename = filename
        self.deck_name = deck_name

    def run(self, ctx: Context):
        if ctx.deck is not None:
            print("Command not supported on Deck Mode")
            return
        cards, errors = validate_txt(self.filename)
        if errors:
            print(f"Found errors in file:\n{'\n'.join(errors)}")
        try:
            deck = deck_service.get_deck_by_name(self.deck_name)
            if deck:
                print(f"Deck {self.deck_name} already exists")
                return
            card_names = [card[1] for card in cards]
            card_data = card_service.get_cards_by_name(card_names)
            if len(card_data) != len(card_names):
                extra_cards = [
                    card.name for card in card_data if card.name not in card_names
                ]
                extra_card_data = card_service.get_many_cards_from_api(extra_cards)
                card_data.extend(extra_card_data)
            print(f"Found {len(card_data)} cards")
            card_list = []
            for card in card_data:
                for qty, name in cards:
                    if card.name == name:
                        card_list.append({"card": card, "quantidade": int(qty)})
                        break
                else:
                    print(f"Card not found: {card.name}")
            deck_service.create_deck_with_cards(self.deck_name, card_list)
            print(f"Deck {self.deck_name} created")
        except Exception as e:
            print(e)
            print("Error importing file")
