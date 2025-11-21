from commom.card_commands import CardCommands
from .base import BaseCommand


class SearchCommand(BaseCommand):
    def __init__(self, query):
        self.query = query

    def run(self, ctx):
        CardCommands.search(self.query)
