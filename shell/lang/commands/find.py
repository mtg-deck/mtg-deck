from .base import BaseCommand


class FindCommand(BaseCommand):
    def __init__(self, query):
        self.query = query

    def run(self, ctx):
        print(f"[find] query={self.query}")
