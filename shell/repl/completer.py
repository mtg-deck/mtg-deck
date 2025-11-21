import os
from prompt_toolkit.completion import Completer, Completion, PathCompleter


ROOT_COMMANDS = [
    "select",
    "cd",
    "create",
    "mk",
    "rename",
    "mv",
    "delete",
    "del",
    "copy",
    "cp",
    "export_all",
    "find",
    "search",
    "exit",
    "clear",
    "cls",
]

DECK_COMMANDS = [
    "add",
    "remove",
    "rmc",
    "reset-commander",
    "set-commander",
    "commander",
    "find",
    "search",
    "export_txt",
    "export_csv",
    "export_json",
    "analize",
    "list",
    "ls",
    "exit",
    "clear",
    "cls",
]


class ShellCompleter(Completer):
    def __init__(self, ctx):
        self.ctx = ctx
        self.path_completer = PathCompleter(expanduser=True)

    def available_commands(self):
        if self.ctx.deck is None:
            return ROOT_COMMANDS
        return DECK_COMMANDS

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()

        commands = self.available_commands()

        if not text:
            for cmd in commands:
                yield Completion(cmd + " ", start_position=0)
            return

        tokens = text.split()
        cmd = tokens[0]

        if len(tokens) == 1:
            word = tokens[0]
            for c in commands:
                if c.startswith(word):
                    yield Completion(c + " ", start_position=-len(word))
            return

        arg = tokens[-1]

        DECKNAME_CMDS_1ARG = ["select", "cd", "export_all"]
        DECKNAME_CMDS_2ARG = ["rename", "mv", "copy", "cp", "delete", "del"]

        if cmd in DECKNAME_CMDS_1ARG:
            for deck in self.ctx.get_deck_names():
                if deck.startswith(arg):
                    yield Completion(deck, start_position=-len(arg))
            return

        if cmd in DECKNAME_CMDS_2ARG:
            for deck in self.ctx.get_deck_names():
                if deck.startswith(arg):
                    yield Completion(deck, start_position=-len(arg))
            return

        CARD_CMDS = ["add", "remove", "rmc", "find", "search", "set-commander"]

        if cmd in CARD_CMDS:
            # cardname
            for card in self.ctx.get_saved_card_names():
                if card.lower().startswith(arg.lower()):
                    yield Completion(card, start_position=-len(arg))
            return

        if cmd in ["export_txt", "export_csv", "export_json", "export_all"]:
            if len(tokens) == 2:
                for p in self.path_completer.get_completions(document, complete_event):
                    yield p
                return

            if len(tokens) == 3:
                for deck in self.ctx.get_deck_names():
                    if deck.startswith(arg):
                        yield Completion(deck, start_position=-len(arg))
                return

        if cmd == "import_txt":
            if len(tokens) == 2:
                for p in self.path_completer.get_completions(document, complete_event):
                    yield p
                return

            if len(tokens) == 3:
                for deck in self.ctx.get_deck_names():
                    if deck.startswith(arg):
                        yield Completion(deck, start_position=-len(arg))
                return

        if cmd in ["list", "ls", "analize"]:
            return
