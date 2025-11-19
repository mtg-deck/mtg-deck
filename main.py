import click
from config import settings
from external.api import get_card_from_api
import service
from tabulate import tabulate

# ---------------------------------------------------------
# Main CLI
# ---------------------------------------------------------

# TODO IMPLEMENT:
# --info
# --get-key
# --logout
# --analyze
# -f e --file
# --commander
# --validade
# --recommend
# --export-txt
# --export-csv
# --export-json
# --export-cb
# --export-decks
# --rename
# --import-folder
# --random
# --random-commander

# DONE:
# -v e --version
# -c e --card
# --list-decks
# --show
# --delete
# --copy


@click.group(invoke_without_command=True)
@click.option("-v", "--version", is_flag=True, help="Show program version.")
@click.option("--info", is_flag=True, help="Show app metadata and config info.")
@click.option("--get-key", is_flag=True, help="Set account key.")
@click.option("--logout", is_flag=True, help="Clear stored credentials.")
@click.option(
    "-f", "--file", type=click.Path(), help="Create a new deck from a .txt file."
)
@click.option("--commander", help="Set commander when creating a new deck.")
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
@click.option("--list-decks", is_flag=True, help="List all saved decks.")
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
@click.pass_context
def cli(ctx, version, card, list_decks, **kwargs):
    """mtg-commander — A CLI deck builder and analyzer for Magic: The Gathering EDH."""
    # print(kwargs)
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
        if kwargs["deck_name"] is None:
            ctx.echo("No deck name provided.")
            ctx.exit()
        ctx.invoke(show_deck, deck_name=kwargs["deck_name"])

    if kwargs["copy"]:
        ctx.invoke(copy_deck, source=kwargs["copy"][0], new=kwargs["copy"][1])

    if kwargs["delete"]:
        ctx.invoke(delete_deck, deck=kwargs["delete"])


@cli.command()
def show_version():
    click.echo(f"mtg-commander {settings.VERSION}")


@cli.command()
@click.argument("deck_name")
def open(deck_name):
    """Open or create a deck."""
    pass


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
    pass


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
    if not settings.user_is_authenticated():
        click.echo("You need to authenticate first. Call --set-key.")
        return
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
@click.argument("path", type=click.Path())
def export_txt(deck_name, path):
    """Export a deck as .txt."""
    pass


@cli.command()
@click.argument("deck_name")
@click.argument("path", type=click.Path())
def export_csv(deck_name, path):
    """Export a deck as .csv."""
    pass


@cli.command()
@click.argument("deck_name")
@click.argument("path", type=click.Path())
def export_json(deck_name, path):
    """Export a deck as .json."""
    pass


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
