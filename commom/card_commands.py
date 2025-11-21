import domain.card_service as card_service
from domain.card import Card
import click
from tabulate import tabulate


class CardCommands:
    def __init__(self, card: Card):
        self.card: Card = card

    @staticmethod
    def search(partial: str):
        try:
            cards = card_service.get_autocomplete_from_api(partial=partial)
            data = [
                [
                    "ID",
                    "Name",
                    "Color",
                    "CMC",
                    "Mana Cost",
                    "Legal Commands",
                    "Is Commander",
                    "Price",
                ]
            ]
            for card in cards:
                data.append(
                    [
                        card.id,
                        card.name,
                        card.colors,
                        card.cmc,
                        card.mana_cost,
                        card.legal_commanders,
                        card.is_commander,
                        card.price,
                    ]
                )
            table = tabulate(data, headers="firstrow")
            click.echo(table)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            raise e

    def __find(self):
        assert self.card is not None
        assert self.card.name is not None
        card = card_service.get_card_by_name(self.card.name)
        if not card:
            raise Exception(f"Card not found: {self.card.name}")
        self.card = card

    @staticmethod
    def from_name(card_name: str):
        try:
            card = CardCommands(Card(name=card_name))
            card.__find()
            return card
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    def show(self):
        table = [
            ["ID", self.card.id if self.card.id is not None else ""],
            ["Name", self.card.name],
            ["Color", self.card.colors],
            ["Color Identity", self.card.color_identity],
            ["CMC", self.card.cmc],
            ["Mana Cost", self.card.mana_cost],
            ["Image URL", self.card.image],
            ["Art URL", self.card.art],
            ["Legal Commands", self.card.legal_commanders],
            ["Is Commander", self.card.is_commander],
            ["Price", self.card.price],
        ]
        table = tabulate(table, headers="firstrow", tablefmt="fancy_grid")
        click.echo(table)
