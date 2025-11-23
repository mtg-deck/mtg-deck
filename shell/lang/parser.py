from lark import Lark
from shell.lang.transformer import CommandTransformer
from pathlib import Path
from infra.config import settings

grammar = Path(settings.BASE_PATH + "/shell/lang/grammar.lark").read_text()
parser = Lark(grammar, parser="lalr")

transformer = CommandTransformer()


def parse_command(input_str):
    tree = parser.parse(input_str)
    return transformer.transform(tree)
