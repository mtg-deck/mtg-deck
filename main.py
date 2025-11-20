import click
import re
from config import settings
from external.api import get_many_cards_from_api
import service
import os
import csv
import json
from tabulate import tabulate
from utils import validate_txt


# =======================================================================
# UTILS & TYPES
# =======================================================================


class TxtFile(click.ParamType):
    name = "txtfile"

    def convert(self, value, param, ctx):
        if not value.lower().endswith(".txt"):
            self.fail("O arquivo deve ser .txt", param, ctx)
        return value


TXT_FILE = TxtFile()


class DeckNameType(click.ParamType):
    name = "deck_name"

    pattern = re.compile(r"^[0-9A-Za-z _+\-]+$")

    def sanitize(self, value):
        return "".join(c for c in value if re.match(r"[0-9A-Za-z _+\-]", c))

    def convert(self, value, param, ctx):
        if not value:
            self.fail("Deck name cannot be empty.", param, ctx)

        sanitized = self.sanitize(value)

        if not self.pattern.match(sanitized):
            self.fail(
                f"Invalid deck name after sanitization: '{sanitized}'",
                param,
                ctx,
            )

        return sanitized


TXT_FILE = TxtFile()
DECK_NAME = DeckNameType()


# =======================================================================
# ROOT COMMAND
# =======================================================================


@click.group()
@click.option("-v", "--version", is_flag=True, help="Show version.")
@click.option("--info", is_flag=True, help="Show metadata.")
@click.option("--get-key", is_flag=True)
@click.option("--logout", is_flag=True)
@click.pass_context
def cli(ctx, version, info, get_key, logout):
    """mtg-commander — EDH deck builder & analyzer."""

    if version:
        click.echo(f"mtg-commander {settings.VERSION}")
        ctx.exit()

    if not settings.user_is_authenticated():
        click.echo("You need to authenticate first (--get-key).")
        ctx.exit()


# =======================================================================
# GROUP: deck
# =======================================================================


@cli.group()
def deck():
    """Manage EDH decks."""
    pass


# -----------------------------------------------------------------------
# deck open/create
# -----------------------------------------------------------------------


@deck.command("open")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("commander", required=False)
def open_or_create(deck_name, commander):
    deck = service.get_deck_by_name(deck_name)

    if deck:
        click.echo(f"Opening deck: {deck_name}")
        return

    click.echo(f"Creating deck: {deck_name}")

    if commander:
        card = service.get_card_by_name(commander)
        if not card:
            click.echo(f"Commander not found: {commander}")
            return
        deck = service.create_deck_with_initial_commander(deck_name, card["id"])
    else:
        deck = service.create_deck(deck_name)

    click.echo(f"Deck created successfully: {deck_name}")


# -----------------------------------------------------------------------
# deck create
# -----------------------------------------------------------------------


@deck.command("create")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("commander", required=False)
def create_deck(deck_name, commander):
    """Create an empty deck or with a commander."""
    deck = service.get_deck_by_name(deck_name)
    if deck:
        click.echo(f"Deck already exists: {deck_name}")
        return

    if commander:
        card = service.get_card_by_name(commander)
        if not card:
            click.echo(f"Commander not found: {commander}")
            return
        service.create_deck_with_initial_commander(deck_name, card["id"])
    else:
        service.create_deck(deck_name)

    click.echo(f"Deck created: {deck_name}")


@deck.command("from-file")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("file", type=TXT_FILE)
def create_deck_from_file(deck_name, file):
    """Create a new deck from a .txt list."""
    deck = service.get_deck_by_name(deck_name)
    if deck:
        click.echo(f"Deck already exists: {deck_name}")
        return

    deck_cards, errors = validate_txt(file)

    if errors:
        click.echo(f"Errors in file: {file}")
        if not click.confirm("Continue with only valid cards?", default=False):
            click.echo("Aborted.")
            return

    click.echo(f"Creating deck: {deck_name}")

    card_list = [card[1] for card in deck_cards]
    try:
        cards = get_many_cards_from_api(card_list)
        if not cards:
            click.echo("No cards found.")
            return
        cards = cards["cards"]
        final_cards = []
        for deck_card in deck_cards:
            for card in cards:
                if deck_card[1] == card["name"]:
                    final_cards.append(
                        {
                            "id": card["id"],
                            "quantidade": deck_card[0],
                            "is_commander": False,
                        }
                    )
                    break
            else:
                click.echo(f"Card not found: {deck_card[1]}")
        click.echo(f"Found {len(cards)} cards.")
        click.echo(f"Adding {len(deck_cards)} cards to deck.")
        service.crete_and_insert_cards(deck_name, final_cards)
        click.echo(f"Deck created successfully: {deck_name}")

    except Exception as e:
        click.echo(f"Error: {e}")


# -----------------------------------------------------------------------
# deck delete
# -----------------------------------------------------------------------


@deck.command("delete")
@click.argument("deck_name", type=DECK_NAME)
def delete_deck(deck_name):
    deck = service.get_deck_by_name(deck_name)
    if not deck:
        click.echo("Deck not found.")
        return

    service.delete_deck(deck[0])
    click.echo(f"Deck deleted: {deck_name}")


# -----------------------------------------------------------------------
# deck rename
# -----------------------------------------------------------------------


@deck.command("rename")
@click.argument("old", type=DECK_NAME)
@click.argument("new", type=DECK_NAME)
def rename_deck(old, new):
    if not service.get_deck_by_name(old):
        click.echo("Original deck not found.")
        return

    if service.get_deck_by_name(new):
        click.echo("Target deck already exists.")
        return

    service.rename_deck(old, new)
    click.echo("Renamed successfully.")


# -----------------------------------------------------------------------
# deck copy
# -----------------------------------------------------------------------


@deck.command("copy")
@click.argument("source", type=DECK_NAME)
@click.argument("new", type=DECK_NAME)
def copy_deck(source, new):
    if not service.get_deck_by_name(source):
        click.echo("Source deck not found.")
        return

    if service.get_deck_by_name(new):
        click.echo("Target deck already exists.")
        return

    service.copy_deck(new, source)
    click.echo(f"Copied: {source} -> {new}")


# -----------------------------------------------------------------------
# deck list
# -----------------------------------------------------------------------


@deck.command("list")
def list_decks():
    decks = service.list_decks()
    table = [["#", "Name", "Commander", "Last Modified"]]

    for d in decks:
        commander = service.get_commander_name_from_deck(d[0])
        table.append([d[0], d[1], commander, d[2]])

    click.echo(tabulate(table, headers="firstrow"))


# -----------------------------------------------------------------------
# deck show
# -----------------------------------------------------------------------


@deck.command("show")
@click.argument("deck_name", type=DECK_NAME)
def show_deck(deck_name):
    deck = service.get_deck_by_name(deck_name)
    if not deck:
        click.echo("Deck not found.")
        return

    cards = service.get_deck_cards(deck[0])
    table = [["Qty", "Card", "Commander"]]

    commanders = [c for c in cards if c[2]]
    normal = [c for c in cards if not c[2]]

    table += commanders + normal
    click.echo(tabulate(table, headers="firstrow"))


# =======================================================================
# deck import/export
# =======================================================================


@deck.group("export")
def deck_export():
    """Export a deck."""
    pass


@deck_export.command("txt")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("path", type=click.Path(exists=True))
def export_txt(deck_name, path):
    cards = service.get_cards_by_deck_name(deck_name)
    output = os.path.join(path, f"{deck_name}.txt")

    with open(output, "w") as f:
        for qty, name, _ in cards:
            f.write(f"{qty} {name}\n")

    click.echo(f"Written: {output}")


@deck_export.command("csv")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("path", type=click.Path(exists=True))
def export_csv(deck_name, path):
    cards = service.get_cards_by_deck_name(deck_name)
    output = os.path.join(path, f"{deck_name}.csv")

    with open(output, "w") as f:
        writer = csv.writer(f)
        for qty, name, _ in cards:
            writer.writerow([qty, name])

    click.echo(f"Written: {output}")


@deck_export.command("json")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("path", type=click.Path(exists=True))
def export_json(deck_name, path):
    cards = service.get_cards_by_deck_name(deck_name)
    output = os.path.join(path, f"{deck_name}.json")

    data = [{"qty": c[0], "name": c[1], "is_commander": c[2]} for c in cards]
    with open(output, "w") as f:
        json.dump(data, f)

    click.echo(f"Written: {output}")


# =======================================================================
# card commands
# =======================================================================


@cli.group()
def card():
    """Card utilities."""
    pass


@card.command("show")
@click.argument("name")
def card_show(name):
    card = service.get_card_by_name(name)
    if not card:
        click.echo("Card not found.")
        return

    for k, v in card.items():
        click.echo(f"{k}: {v}")


# =======================================================================
# random commands
# =======================================================================


@cli.group()
def random():
    """Random cards/commanders."""
    pass


@random.command("card")
@click.option("--count", type=int, default=1)
def random_card(count):
    pass


@random.command("commander")
def random_commander():
    pass


# =======================================================================

if __name__ == "__main__":
    cli()
