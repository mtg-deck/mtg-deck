import click
import re
from commom.card_commands import CardCommands
from commom.deck_list_commands import DeckListCommands
from infra.config import settings
from commom.utils import clear_screen
from commom.validators import validate_path
from shell.repl.repl import repl
from commom.deck_commands import DeckCommands
from commom.deck_card_commands import DeckCardCommands

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
    cmd = DeckCommands.from_name(deck_name)
    if not cmd:
        click.echo("Deck not found.")
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
def delete_deck(deck_name):
    cmd = DeckCommands.from_name(deck_name)
    cmd.delete()


# -----------------------------------------------------------------------
# deck rename
# -----------------------------------------------------------------------


@deck.command("rename")
@click.argument("old", type=DECK_NAME)
@click.argument("new", type=DECK_NAME)
def rename_deck(old, new):
    cmd = DeckCommands.from_name(old)
    cmd.rename(new)


# -----------------------------------------------------------------------
# deck copy
# -----------------------------------------------------------------------


@deck.command("copy")
@click.argument("source", type=DECK_NAME)
@click.argument("new", type=DECK_NAME)
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
def show_deck(deck_name):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    if not cmd:
        click.echo("Deck not found.")
    cmd.show()


# =======================================================================
# deck commander
# =======================================================================


@deck.command("set-commander")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("commander", type=DECK_NAME)
def set_commander(deck_name, commander):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    if not cmd:
        return
    cmd.set_commander(commander)


@deck.command("reset-commander")
@click.argument("deck_name", type=DECK_NAME)
def reset_commander(deck_name):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    if not cmd:
        return
    cmd.reset_commander()


# =======================================================================
# deck cards
# =======================================================================


@deck.command("add")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("card_name", type=DECK_NAME)
@click.argument("qty", type=int, required=False, default=1)
def deck_add_card(deck_name, card_name, qty):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    if not cmd:
        return
    cmd.add(card_name, qty)


@deck.command("remove")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("card_name", required=True)
@click.argument("qty", type=int, required=False, default=1)
def deck_remove_card(deck_name, card_name, qty):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    if not cmd:
        return
    cmd.remove(card_name, qty)


@deck.command("set")
@click.argument("deck_name", type=DECK_NAME)
@click.argument("card_name", required=True)
@click.option("--qty", type=int, required=False, default=1)
def deck_set_card_qty(deck_name, card_name, qty):
    cmd = DeckCardCommands.from_deck_name(deck_name)
    if not cmd:
        return
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
def card_show(name):
    cmd = CardCommands.from_name(name)
    if not cmd:
        click.echo("Card not found.")
        return
    cmd.show()


@card.command("search")
@click.argument("partial", type=str)
def card_search(partial):
    CardCommands.search(partial)


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
