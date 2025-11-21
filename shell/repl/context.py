from shell.domain.deck import Deck


class Context:
    def __init__(self, deck=None, deck_cards=None):
        assert isinstance(deck, Deck | None)
        assert isinstance(deck_cards, list | None)

        self.deck = deck
        self.deck_cards = deck_cards

    def set_deck(self, deck):
        assert isinstance(deck, Deck | None)
        self.deck = deck

    def set_deck_cards(self, deck_cards):
        assert isinstance(deck_cards, list | None)
        self.deck_cards = deck_cards
