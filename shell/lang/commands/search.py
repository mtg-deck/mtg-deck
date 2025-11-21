from .base import BaseCommand


class SearchCommand(BaseCommand):
    def __init__(self, query):
        self.query = query

    def run(self, ctx):
        print(f"[search] query={self.query}")
