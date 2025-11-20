import click
from config import settings
import service
from tabulate import tabulate
import os
import csv
import json

# ---------------------------------------------------------
# Main CLI
# ---------------------------------------------------------

# TODO IMPLEMENT:
# --info
# --get-key
# --logout
# --analyze
# -f e --file
# --validade
# --recommend
# --export-cb
# --export-decks
# --import-folder
# --random
# --random-commander

# DONE:
# --rename
# -v e --version
# -c e --card
# --list-decks e --list
# --show
# --delete
# --copy
# --export-txt
# --export-csv
# --export-json
# --commander


@click.group(invoke_without_command=True)
@click.option("-v", "--version", is_flag=True, help="Show program version.")
@click.option("--info", is_flag=True, help="Show app metadata and config info.")
@click.option("--get-key", is_flag=True, help="Set account key.")
@click.option("--logout", is_flag=True, help="Clear stored credentials.")
@click.option(
    "-f", "--file", type=click.Path(), help="Create a new deck from a .txt file."
)
@click.option(
    "--analyze", is_flag=True, help="Analyze the deck without launching the UI."
)
@click.option("--validade", is_flag=True, help="Validate a Commander deck.")
@click.option("-c", "--card", help="Analyze a single card (only without a deck/file).")
@click.option("--recommend", is_flag=True, help="Provide card recommendations.")
@click.option("--export-txt", type=click.Path(), help="Export deck as .txt.")
@click.option("--export-csv", type=click.Path(), help="Export deck as .csv.")
@click.option("--export-json", type=click.Path(), help="Export deck as .json.")
@click.option("--export-cb", is_flag=True, help="Export deck to clipboard.")
@click.option("--export-decks", type=click.Path(), help="Export all decks as .zip.")
@click.option("--list-decks", "--list", is_flag=True, help="List all saved decks.")
@click.option("--show", is_flag=True, help="Show deck on console.")
@click.option("--delete", help="Delete a deck.")
@click.option("--rename", nargs=2, help="Rename a deck: <old> <new>.")
@click.option("--copy", nargs=2, help="Copy a deck: <source> <new>.")
@click.option(
    "--import-folder", type=click.Path(), help="Import all .txt decks from a folder."
)
@click.option("--random", "random_n", type=int, help="Fetch N random cards.")
@click.option(
    "--random-commander", is_flag=True, help="Fetch a random legal Commander."
)
@click.argument("deck_name", required=False)
@click.argument("commander", required=False)
@click.pass_context
def cli(ctx, version, card, list_decks, deck_name, **kwargs):
    """mtg-commander — A CLI deck builder and analyzer for Magic: The Gathering EDH."""
    if not settings.user_is_authenticated():
        click.echo("You need to authenticate first. Call --set-key.")
        return
    print(kwargs)
    ctx.ensure_object(dict)
    ctx.obj["options"] = kwargs

    if version:
        ctx.invoke(show_version)
        ctx.exit()

    if card:
        ctx.invoke(show_card, card_name=card)
        ctx.exit()

    if list_decks:
        ctx.invoke(list_all_decks)
        ctx.exit()

    if kwargs["show"]:
        if deck_name is None:
            ctx.echo("No deck name provided.")
            ctx.exit()
        ctx.invoke(show_deck, deck_name=deck_name)
        ctx.exit()

    if kwargs["copy"]:
        ctx.invoke(copy_deck, source=kwargs["copy"][0], new=kwargs["copy"][1])
        ctx.exit()

    if kwargs["delete"]:
        ctx.invoke(delete_deck, deck=kwargs["delete"])
        ctx.exit()

    if kwargs["export_txt"]:
        ctx.invoke(export_txt, deck_name=deck_name, path=kwargs["export_txt"])
        ctx.exit()

    if kwargs["export_csv"]:
        ctx.invoke(export_csv, deck_name=deck_name, path=kwargs["export_csv"])
        ctx.exit()

    if kwargs["export_json"]:
        ctx.invoke(export_json, deck_name=deck_name, path=kwargs["export_json"])
        ctx.exit()

    if kwargs["rename"]:
        ctx.invoke(rename, old=kwargs["rename"][0], new=kwargs["rename"][1])
        ctx.exit()

    if deck_name:
        ctx.invoke(open_or_create, deck_name=deck_name, commander=kwargs["commander"])


@cli.command()
def show_version():
    click.echo(f"mtg-commander {settings.VERSION}")


@cli.command()
@click.argument("deck_name")
@click.argument("commander", required=False)
def open_or_create(deck_name, commander=None):
    """Open or create a deck."""
    try:
        deck = service.get_deck_by_name(deck_name)
    except Exception as e:
        click.echo(f"Error fetching deck: {e}")
        return
    if deck:
        click.echo(f"Opening deck: {deck_name}")
    else:
        click.echo(f"Creating deck: {deck_name}")
        if commander:
            try:
                card = service.get_card_by_name(commander)
                if not card:
                    click.echo(f"Commander not found: {commander}")
                    click.echo("Aborting")
                    return
                deck = service.create_deck_with_initial_commander(deck_name, card["id"])
                click.echo(f"Deck created successfully: {deck_name}")
            except Exception as e:
                click.echo(f"Error creating deck: {e}")
        else:
            try:
                deck = service.create_deck(deck_name)
                click.echo(f"Deck created successfully: {deck_name}")
            except Exception as e:
                click.echo(f"Error creating deck: {e}")
        return


@cli.command()
def list_all_decks():
    """List all saved decks."""
    decks = service.list_decks()
    table = [["#", "Name", "Commander", "Last Modified"]]
    for deck in decks:
        commander = service.get_commander_name_from_deck(deck[0])
        table.append([deck[0], deck[1], commander, deck[2]])
    click.echo(tabulate(table, headers="firstrow"))


@cli.command()
@click.argument("deck")
def delete_deck(deck):
    """Delete a deck."""
    deck_row = service.get_deck_by_name(deck)
    if not deck_row:
        click.echo(f"Deck not found: {deck}")
        return
    try:
        service.delete_deck(deck_row[0])
        click.echo(f"Deck deleted successfully: {deck}")
    except Exception as e:
        click.echo(f"Error deleting deck: {e}")


@cli.command()
@click.argument("old")
@click.argument("new")
def rename(old, new):
    """Rename a deck."""
    deck_old = service.get_deck_by_name(old)
    if not deck_old:
        click.echo(f"Deck not found: {old}")
        return
    deck_new = service.get_deck_by_name(new)
    if deck_new:
        click.echo(f"Deck already exists: {new}")
        return
    click.echo("Renaming %s to %s" % (old, new))
    try:
        service.rename_deck(old, new)
        click.echo("Deck renamed successfully.")
    except Exception as e:
        click.echo(f"Error renaming deck: {e}")


@cli.command()
@click.argument("source")
@click.argument("new")
def copy_deck(source, new):
    """Duplicate a deck."""
    old_deck = service.get_deck_by_name(source)
    if not old_deck:
        click.echo(f"Deck not found: {source}")
        return
    new_deck = service.get_deck_by_name(new)
    if new_deck:
        click.echo(f"Deck already exists: {new}")
        return
    click.echo("Copying %s to %s" % (source, new))
    try:
        service.copy_deck(new, source)
        click.echo("Deck copied successfully.")
        click.echo(f"To see the new deck, run: mtg-commander --show {new}")
    except Exception as e:
        click.echo(f"Error copying deck: {e}")


@cli.command()
@click.argument("path", type=click.Path())
def import_folder(path):
    """Import all .txt decks from a directory."""
    pass


@cli.command()
@click.option("--count", type=int, default=1, help="Number of random cards.")
def random(count):
    """Fetch N random Magic cards."""
    pass


@cli.command()
def random_commander():
    """Fetch a random legal Commander."""
    pass


def show_deck(deck_name):
    """Show a deck on console."""
    deck = service.get_deck_by_name(deck_name)
    if not deck:
        click.echo(f"Deck not found: {deck_name}")
        return
    cards = service.get_deck_cards(deck[0])
    table = [["Amount", "Card", "Commander"]]
    commander = []
    rest = []
    for card in cards:
        if card[2] == "COMMANDER":
            commander.append(card)
            continue
        rest.append(card)
    table = table + commander + rest
    click.echo(tabulate(table, headers="firstrow"))


# ---------------------------------------------------------
# Analysis Subcommands
# ---------------------------------------------------------


@cli.command()
@click.argument("deck_name")
def analyze(deck_name):
    """Analyze a deck."""
    pass


@cli.command()
@click.argument("deck_name")
def validade(deck_name):
    """Validate a Commander deck."""
    pass


@click.argument("card_name")
def show_card(card_name):
    """Analyze a single card."""
    try:
        card = service.get_card_by_name(card_name)
        if not card:
            click.echo(f"Card not found: {card_name}")
            return
        for key, value in card.items():
            click.echo(f"{key}: {value}")
    except Exception as e:
        if e.args[0] == "HTTP error fetching card: 404":
            click.echo(f"Card not found: {card_name}")
        else:
            click.echo(f"Error fetching card: {e}")


@cli.command()
@click.argument("deck_name")
def recommend(deck_name):
    """Provide card recommendations for a deck."""
    pass


# ---------------------------------------------------------
# Export Commands
# ---------------------------------------------------------


@cli.command()
@click.argument("deck_name")
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def export_txt(deck_name, path):
    """Export a deck as .txt."""
    cards = service.get_cards_by_deck_name(deck_name)
    card_list = []
    for card in cards:
        if card[2]:
            card_list.insert(0, f"{card[0]} {card[1]}")
            continue
        card_list.append(f"{card[0]} {card[1]}")

    full_path = os.path.join(path, f"{deck_name}.txt")
    with click.open_file(full_path, "w") as f:
        f.write("\n".join(card_list) + "\n")

    click.echo(f"Escrito em {full_path}")


@cli.command()
@click.argument("deck_name")
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def export_csv(deck_name, path):
    """Exporta um deck em formato CSV."""
    cards = service.get_cards_by_deck_name(deck_name)

    commanders = [card for card in cards if card[2]]
    non_commanders = [card for card in cards if not card[2]]

    ordered_cards = commanders + non_commanders

    if os.path.isdir(path):
        full_path = os.path.join(path, f"{deck_name}.csv")
    else:
        full_path = path

    with click.open_file(full_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        for qty, name, _ in ordered_cards:
            writer.writerow([qty, name])

    click.echo(f"Escrito em {full_path}")


@cli.command()
@click.argument("deck_name")
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def export_json(deck_name, path):
    """Export a deck as .json."""
    cards = service.get_cards_by_deck_name(deck_name)

    commanders = [card for card in cards if card[2]]
    non_commanders = [card for card in cards if not card[2]]

    ordered_cards = commanders + non_commanders

    cards_json = [
        {"qty": card[0], "name": card[1], "is_commander": card[2]}
        for card in ordered_cards
    ]
    full_path = os.path.join(path, f"{deck_name}.json")

    with click.open_file(full_path, "w") as f:
        json.dump(cards_json, f)


@cli.command()
@click.argument("deck_name")
def export_cb(deck_name):
    """Export a deck to clipboard."""
    pass


@cli.command()
@click.argument("path", type=click.Path())
def export_decks(path):
    """Export all decks into a zip archive."""
    pass


# ---------------------------------------------------------
# User & Auth
# ---------------------------------------------------------


@cli.command()
def get_key():
    """Set the account key."""
    pass


@cli.command()
def logout():
    """Clear stored credentials."""
    pass


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    cli()
