from .base import BaseCommand
from commom.top_commanders_commands import TopCommandersCommands


class TopCommandersCommand(BaseCommand):
    def run(self, ctx):
        TopCommandersCommands.show_top_commanders_shell()

