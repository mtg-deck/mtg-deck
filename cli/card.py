"""
Comandos relacionados a cards.
"""
import click
from commom.card_commands import CardCommands
from commom.top_commanders_commands import TopCommandersCommands
from .utils import handle_cli_exceptions


def register_card_commands(cli_group):
    """Registra todos os comandos relacionados a cards."""
    
    @cli_group.group()
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

