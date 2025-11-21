import click
import re
from shell.infra.config import settings
from shell.external.api import get_many_cards_from_api
import service
import os
import csv
import json
from tabulate import tabulate
from utils import validate_txt, clear_screen
from shell.repl.repl import repl

# TODO: Implementar random_card (gerar cartas aleatórias)
# TODO: Implementar random_commander (gerar comandante aleatório)
# TODO: Adicionar validação extra no DECK_NAME para tamanho máximo/único
# TODO: Melhorar create_deck_from_file — validar commander dentro do .txt
# TODO: Implementar exportação padronizada com commander no topo
# TODO: Criar comandos de import (moxfield/archidekt/etc)
# TODO: Criar comando para atualizar quantidade (deck set-qty)
# TODO: Criar comando search de cards no CLI
# TODO: Mover prints para flags opcionais (--verbose, --quiet)
# TODO: Melhorar card_show com formatação/tabulação
# TODO: Adicionar comando deck stats (cores, curva de mana, etc)
# TODO: Criar comando deck price (somar preços)
# TODO: Sincronizar banco com API (update-cards)
# TODO: Validar que a pasta do export é gravável (não só exists=True)
# TODO: Criar um comando global config para API key, temas, preferências
# TODO: Adicionar opção --force no delete/copy/rename
# TODO: Permitir shorthand para deck_name (ex: completar parcial)
# TODO: Adicionar testes unitários dos comandos
# TODO: Garantir consistência dos tipos de retorno (service layer)

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

    if not click.confirm(f"Are you sure you want to delete {deck_name}?", default=True):
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

    if not click.confirm(
        f"Are you sure you want to rename {old} to {new}?", default=True
    ):
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

    if not click.confirm(
        f"Are you sure you want to copy {source} to {new}?", default=True
    ):
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

    click.echo_via_pager(tabulate(table, headers="firstrow"))


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
# deck commander
# =======================================================================


@deck.command("set-commander")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("commander", type=DECK_NAME)
@click.option("--force", is_flag=True)
def set_commander(deck_name, commander, force):
    deck = service.get_deck_by_name(deck_name)
    if not deck:
        click.echo(f"Deck not found: {deck_name}")
        return
    try:
        current_commander = service.get_commander_name_from_deck(deck[0])
        if current_commander:
            if not force and not click.confirm(
                f"Do you want to remove {current_commander} as commander of deck {deck_name}?",
                default=True,
            ):
                click.echo("Aborted.")
                return
            click.echo(
                f"Removing {current_commander} as commander of deck {deck_name}."
            )
        click.echo(f"Setting {commander} as commander of deck {deck_name}.")
        commander = service.get_card_by_name(commander)
        if not commander:
            click.echo(f"Commander not found: {commander}")
            return
        service.set_commander(deck[0], commander["id"])
    except Exception as e:
        click.echo(f"Error fetching commander: {e}")


@deck.command("reset-commander")
@click.argument("deck_name", type=DECK_NAME)
@click.option("--force", is_flag=True)
def reset_commander(deck_name, force):
    deck = service.get_deck_by_name(deck_name)
    if not deck:
        click.echo(f"Deck not found: {deck_name}")
        return
    try:
        current_commander = service.get_commander_name_from_deck(deck[0])
        if not current_commander:
            click.echo(f"Deck {deck_name} has no commander.")
            return
        if not force and not click.confirm(
            f"Are you sure you want to remove {current_commander} as commander of deck {deck_name}?",
            default=True,
        ):
            click.echo("Aborted.")
            return
        click.echo(f"Removing {current_commander} as commander of deck {deck_name}.")
        service.reset_commander_of_deck(deck[0])
    except Exception as e:
        click.echo(f"Error resetting commander: {e}")


# =======================================================================
# deck cards
# =======================================================================


@deck.command("add-card")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("card_name", type=DECK_NAME)
@click.option("--qty", type=int, required=False, default=1)
def deck_add_card(deck_name, card_name, qty):
    if qty == 0:
        click.echo("Cannot add 0 cards.")
        return
    if qty < 0:
        click.echo(
            "Cannot add negative cards, to remove cards use the remove-card command."
        )
        return
    try:
        deck = service.get_deck_by_name(deck_name)
        if not deck:
            click.echo(f"Deck not found: {deck_name}")
            return
        deck_card = service.get_deck_card_by_deck_and_card_name(deck_name, card_name)
        if deck_card and deck_card[3]:
            click.echo("Cannot add more than one commander to a deck.")
            return
        card = service.get_card_by_name(card_name)
        if not card:
            click.echo(f"Card not found: {card_name}")
            return
        service.add_card_to_deck(deck[0], card["id"], qty)
        click.echo(f"Added {qty} x {card_name} to deck {deck_name}.")

        qty = qty + deck_card[2] if deck_card else 0

        click.echo(f"Deck {deck_name} has {qty} x {card_name} remaining.")

    except Exception as e:
        click.echo(f"Error adding card: {e}")


@deck.command("remove-card")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("card_name", required=True)
@click.option("--qty", type=int, required=False, default=1)
@click.option("--force", is_flag=True)
def deck_remove_card(deck_name, card_name, qty, force):
    if qty == 0:
        click.echo("Cannot remove 0 cards.")
        return
    if qty < 0:
        click.echo(
            "Cannot remove negative cards, to add cards use the add-card command."
        )
        return
    qty = -qty
    try:
        deck = service.get_deck_by_name(deck_name)
        if not deck:
            click.echo(f"Deck not found: {deck_name}")
            return

        deck_card = service.get_deck_card_by_deck_and_card_name(deck_name, card_name)
        if not deck_card:
            click.echo(f"Card not found on deck: {card_name}")
            return

        if deck_card[3]:
            click.echo(f"{card_name} is a commander.")
            if not force and not click.confirm(
                "Do you want to remove the commander?", default=True
            ):
                click.echo("Aborted.")
                return

        if -qty >= deck_card[2]:
            click.echo(f"Deck has only {deck_card[2]} x {card_name}.")
            if not force and not click.confirm(
                "Do you want to remove all cards?", default=True
            ):
                click.echo("Aborted.")
                return
            click.echo(f"Removing all {card_name} from deck {deck_name}.")
            service.remove_card_from_deck(deck[0], deck_card[1])
            click.echo(f"Removed all {card_name} from deck {deck_name}.")
            return

        click.echo(f"Removing {-qty} x {card_name} from deck {deck_name}.")
        service.add_card_to_deck(deck[0], deck_card[1], qty)

        remaining = deck_card[2] + qty

        click.echo(f"Deck {deck_name} has {remaining} x {card_name} remaining.")

    except Exception as e:
        click.echo(f"Error adding card: {e}")


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
# shell
# =======================================================================


@cli.command()
def shell():
    """Run a shell."""
    clear_screen()
    repl()


# =======================================================================

if __name__ == "__main__":
    cli()
