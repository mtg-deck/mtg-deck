import click
from config import settings
from external.api import get_card_from_api

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
# --list-decks
# --delete
# --rename
# --copy
# --import-folder
# --random
# --random-commander

# DONE:
# -v e --version
# -c e --card


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
def cli(ctx, version, card, **kwargs):
    """mtg-commander — A CLI deck builder and analyzer for Magic: The Gathering EDH."""
    ctx.ensure_object(dict)
    ctx.obj["options"] = kwargs

    if version:
        ctx.invoke(show_version)
        ctx.exit()

    if card:
        ctx.invoke(show_card, card_name=card)
        ctx.exit()


@cli.command()
def show_version():
    click.echo(f"mtg-commander {settings.VERSION}")


# ---------------------------------------------------------
# Subcommands (optional grouping if you want)
# ---------------------------------------------------------


@cli.command()
@click.argument("deck_name")
def open(deck_name):
    """Open or create a deck."""
    pass


@cli.command()
def list_decks():
    """List all saved decks."""
    pass


@cli.command()
@click.argument("deck")
def delete(deck):
    """Delete a deck."""
    pass


@cli.command()
@click.argument("old")
@click.argument("new")
def rename(old, new):
    """Rename a deck."""
    pass


@cli.command()
@click.argument("source")
@click.argument("new")
def copy(source, new):
    """Duplicate a deck."""
    pass


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


@cli.command()
@click.argument("card_name")
def show_card(card_name):
    """Analyze a single card."""
    if not settings.user_is_authenticated():
        click.echo("You need to authenticate first. Call --set-key.")
        return
    try:
        card = get_card_from_api(card_name)
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
