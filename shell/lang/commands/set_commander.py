from .base import BaseCommand


class SetCommanderCommand(BaseCommand):
    def __init__(self, name):
        self.name = name

    def run(self, ctx):
        print(f"[set-commander] name={self.name}")
