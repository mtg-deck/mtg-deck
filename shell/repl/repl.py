from prompt_toolkit import PromptSession
from shell.lang.parser import transformer, parser
from .context import Context

session = PromptSession()


def repl():
    ctx = Context()

    while True:
        try:
            s = "> "
            if ctx.deck:
                s = f"{ctx.deck.name} > "
            line = session.prompt(s)
            if not line:
                continue

            tree = parser.parse(line)
            cmd = transformer.transform(tree)
            cmd.run(ctx)

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


if __name__ == "__main__":
    repl()
