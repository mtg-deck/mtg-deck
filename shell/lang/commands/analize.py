from .base import BaseCommand


class AnalizeCommand(BaseCommand):
    def __init__(self, name):
        self.name = name

    def run(self, ctx):
        print(f"[analize] name={self.name}")
