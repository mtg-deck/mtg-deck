from lark import Lark
from shell.lang.transformer import CommandTransformer
from pathlib import Path

grammar = Path(__file__).with_name("grammar.lark").read_text()
parser = Lark(grammar, parser="lalr")

transformer = CommandTransformer()


def parse_command(input_str):
    tree = parser.parse(input_str)
    return transformer.transform(tree)
