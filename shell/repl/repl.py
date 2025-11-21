from prompt_toolkit import PromptSession
from shell.lang.parser import transformer, parser
from .context import Context
from prompt_toolkit.completion import Completer
from .completer import ShellCompleter

session = PromptSession()


def repl():
    ctx = Context()
    completer = ShellCompleter(ctx)

    count = 1

    while True:
        try:
            s = f"[ {count} ] > "
            if ctx.deck:
                s = f"[ {count} ] : [ {ctx.deck.name} ] > "

            line = session.prompt(s, completer=completer)

            if not line:
                continue

            tree = parser.parse(line)
            cmd = transformer.transform(tree)
            cmd.run(ctx)

            count += 1
            print("\n")

        except KeyboardInterrupt:
            print("\nbye")
            break

        except SystemExit:
            print("\nbye")
            break

        except EOFError:
            print("\nbye")
            break

        except Exception as e:
            print("Erro:", e)
