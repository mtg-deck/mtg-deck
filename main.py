import click
import subprocess
import re
from functools import wraps
from commom.card_commands import CardCommands
from commom.deck_list_commands import DeckListCommands
from infra.config import settings
from commom.utils import clear_screen
from commom.validators import validate_path
from shell.repl.repl import repl
from commom.deck_commands import DeckCommands
from commom.deck_card_commands import DeckCardCommands
from commom.commander_meta_commands import CommanderMetaCommands
from commom.top_commanders_commands import TopCommandersCommands
from commom.exception_handler import cli_handler
from commom.excptions import (
    CardNotFound,
    DeckNotFound,
    DeckAlreadyExists,
    CardNotOnDeck,
    CardIsCommander,
    ShortPartial,
    InvalidQuantity,
)
import webbrowser

# TODO: Melhorar create_deck_from_file — validar commander dentro do .txt
# TODO: Criar comando para atualizar quantidade (deck set-qty)
# TODO: Criar comando search de cards no CLI
# TODO: Mover prints para flags opcionais (--verbose, --quiet)
# TODO: Melhorar card_show com formatação/tabulação
# TODO: Adicionar comando deck stats (cores, curva de mana, etc)
# TODO: Criar comando deck price (somar preços)
# TODO: Sincronizar banco com API (update-cards)
# TODO: Criar um comando global config para API key, temas, preferências
# TODO: Permitir shorthand para deck_name (ex: completar parcial)
# TODO: Adicionar testes unitários dos comandos
# TODO: Garantir consistência dos tipos de retorno (service layer)

# =======================================================================
# UTILS & TYPES
# =======================================================================


def handle_cli_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (
            CardNotFound,
            DeckNotFound,
            DeckAlreadyExists,
            CardNotOnDeck,
            CardIsCommander,
            ShortPartial,
            InvalidQuantity,
        ) as e:
            cli_handler.handle(e)
            return
        except Exception as e:
            click.echo(f"Unexpected error: {e}", err=True)
            raise
    return wrapper


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
@handle_cli_exceptions
def open_or_create(deck_name, commander):
    cmd = DeckCommands.from_name(deck_name)
    if not cmd.exists():
        click.echo(f"Creating deck '{deck_name}'...")
        if commander:
            cmd.create_with_commander(commander)
        else:
            cmd.create()
    click.echo(f"Opening deck '{deck_name}'...")


# -----------------------------------------------------------------------
# deck create
# -----------------------------------------------------------------------


@deck.command("create")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("commander", required=False)
@handle_cli_exceptions
def create_deck(deck_name, commander):
    """Create an empty deck or with a commander."""
    cmd = DeckCommands.from_name(deck_name)
    if commander:
        cmd.create_with_commander(commander)
    else:
        cmd.create()


@deck.command("import-txt")
@click.argument("file", type=TXT_FILE)
@click.argument("deck_name", type=DECK_NAME)
@handle_cli_exceptions
def create_deck_from_file(deck_name, file):
    """Create a new deck from a .txt list."""
    if not validate_path(file, ".txt"):
        return
    cmd = DeckCommands.from_name(deck_name)
    cmd.import_txt(file)


# -----------------------------------------------------------------------
# deck delete
# -----------------------------------------------------------------------


@deck.command("delete")
@click.argument("deck_name", type=DECK_NAME)
@handle_cli_exceptions
def delete_deck(deck_name):
    cmd = DeckCommands.from_name(deck_name)
    cmd.delete()


# -----------------------------------------------------------------------
# deck rename
# -----------------------------------------------------------------------


@deck.command("rename")
@click.argument("old", type=DECK_NAME)
@click.argument("new", type=DECK_NAME)
@handle_cli_exceptions
def rename_deck(old, new):
    cmd = DeckCommands.from_name(old)
    cmd.rename(new)


# -----------------------------------------------------------------------
# deck copy
# -----------------------------------------------------------------------


@deck.command("copy")
@click.argument("source", type=DECK_NAME)
@click.argument("new", type=DECK_NAME)
@handle_cli_exceptions
def copy_deck(source, new):
    cmd = DeckCommands.from_name(source)
    cmd.copy(new)


# -----------------------------------------------------------------------
# deck list
# -----------------------------------------------------------------------


@deck.command("list")
@click.argument("limit", type=int, required=False)
def list_decks(limit):
    DeckListCommands.show(limit)


# -----------------------------------------------------------------------
# deck show
# -----------------------------------------------------------------------


@deck.command("show")
@click.argument("deck_name", type=DECK_NAME)
@handle_cli_exceptions
def show_deck(deck_name):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    cmd.show()


# =======================================================================
# deck commander
# =======================================================================


@deck.command("set-commander")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("commander", type=DECK_NAME)
@handle_cli_exceptions
def set_commander(deck_name, commander):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    cmd.set_commander(commander)


@deck.command("reset-commander")
@click.argument("deck_name", type=DECK_NAME)
@handle_cli_exceptions
def reset_commander(deck_name):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    cmd.reset_commander()


# =======================================================================
# deck meta
# =======================================================================


@deck.command("meta")
@click.argument("commander_name", type=str)
@click.argument("category", type=str, required=False)
@handle_cli_exceptions
def deck_meta(commander_name, category):
    """Get meta cards for a commander from EDHREC."""
    CommanderMetaCommands.get_meta(commander_name, category)


# =======================================================================
# deck cards
# =======================================================================


@deck.command("add")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("card_name", type=DECK_NAME)
@click.argument("qty", type=int, required=False, default=1)
@handle_cli_exceptions
def deck_add_card(deck_name, card_name, qty):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    cmd.add(card_name, qty)


@deck.command("remove")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("card_name", required=True)
@click.argument("qty", type=int, required=False, default=1)
@handle_cli_exceptions
def deck_remove_card(deck_name, card_name, qty):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    cmd.remove(card_name, qty)


@deck.command("set")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("card_name", required=True)
@click.option("--qty", type=int, required=False, default=1)
@handle_cli_exceptions
def deck_set_card_qty(deck_name, card_name, qty):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    cmd.edit_quantity(card_name, qty)


# =======================================================================
# deck import/export
# =======================================================================


@cli.group("export")
def deck_export():
    """Export a deck."""
    pass


@deck_export.command("txt")
@click.argument("deck_name", type=DECK_NAME)
@click.argument(
    "path",
    type=click.Path(
        exists=True, dir_okay=True, file_okay=False, writable=True, readable=True
    ),
)
@handle_cli_exceptions
def export_txt(deck_name, path):
    if not validate_path(path):
        return
    cmd = DeckCommands.from_name(deck_name)
    cmd.export_txt(path)


@deck_export.command("csv")
@click.argument("deck_name", type=DECK_NAME)
@click.argument(
    "path",
    type=click.Path(
        exists=True, dir_okay=True, file_okay=False, writable=True, readable=True
    ),
)
@handle_cli_exceptions
def export_csv(deck_name, path):
    if not validate_path(path):
        return
    cmd = DeckCommands.from_name(deck_name)
    cmd.export_csv(path)


@deck_export.command("json")
@click.argument("deck_name", type=DECK_NAME)
@click.argument(
    "path",
    type=click.Path(
        exists=True, dir_okay=True, file_okay=False, writable=True, readable=True
    ),
)
@handle_cli_exceptions
def export_json(deck_name, path):
    if not validate_path(path):
        return
    cmd = DeckCommands.from_name(deck_name)
    cmd.export_json(path)


@deck_export.command("all")
@click.argument(
    "path",
    type=click.Path(
        exists=True, dir_okay=True, file_okay=False, readable=True, writable=True
    ),
)
def export_all(path):
    DeckListCommands.export_folder(path)
    click.echo(f"Exported everything to {path}")


# =======================================================================
# card commands
# =======================================================================


@cli.group()
def card():
    """Card utilities."""
    pass


@card.command("find")
@click.argument("name")
@handle_cli_exceptions
def card_show(name):
    cmd = CardCommands.from_name(name)
    cmd.show()


@card.command("search")
@click.argument("partial", type=str)
@handle_cli_exceptions
def card_search(partial):
    CardCommands.search(partial)


@card.command("top-commanders")
@handle_cli_exceptions
def top_commanders():
    """List the top 100 commanders."""
    TopCommandersCommands.show_top_commanders()


# =======================================================================
# shell
# =======================================================================


@cli.command()
def shell():
    """Run a shell."""
    clear_screen()
    repl()


# =======================================================================
# shell
# =======================================================================


@cli.command()
def start_editor():
    """Inicia o editor."""

    BACKEND_CMD = [
        "uvicorn",
        "editor.backend.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "3839",
        "--reload",
        # "--log-level",
        # "warning",
    ]

    # FRONTEND_CMD = ["python", "-m", "http.server", "3938"]
    # frontend = subprocess.Popen(FRONTEND_CMD, cwd="editor/frontend")

    backend = subprocess.Popen(BACKEND_CMD)
    # frontend = subprocess.Popen(FRONTEND_CMD)
    webbrowser.open("0.0.0.0:3839")

    click.echo(f"Backend PID: {backend.pid}")
    # click.echo(f"Frontend PID: {frontend.pid}")

    try:
        backend.wait()
        # frontend.wait()
    except KeyboardInterrupt:
        click.echo("\nEncerrando...")
    finally:
        backend.terminate()
        # frontend.terminate()
        backend.wait()
        # frontend.wait()
        click.echo("Finalizado.")


# =======================================================================

if __name__ == "__main__":
    from infra.init_db import init_db

    init_db()
    cli()
