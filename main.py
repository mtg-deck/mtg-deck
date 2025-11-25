"""
Entry point principal - apenas comandos básicos (shell, editor, version).
Comandos CLI completos estão em cli/
"""

try:
    from cli import cli
except ImportError:
    import click
    import subprocess
    import webbrowser
    from infra.config import settings
    from commom.utils import clear_screen
    from shell.repl.repl import repl

    @click.group()
    @click.option("-v", "--version", is_flag=True, help="Show version.")
    @click.option("--info", is_flag=True, help="Show metadata.")
    @click.option("--get-key", is_flag=True)
    @click.option("--logout", is_flag=True)
    @click.pass_context
    def cli(ctx, version, info, get_key, logout):
        """edhelper — EDH deck builder & analyzer."""

        if version:
            click.echo(f"edhelper {settings.VERSION}")
            ctx.exit()

        if not settings.user_is_authenticated():
            click.echo("You need to authenticate first (--get-key).")
            ctx.exit()

    @cli.command()
    def shell():
        """Run a shell."""
        clear_screen()
        repl()

    @cli.command()
    def start_editor():
        """Inicia o editor."""

        BACKEND_CMD = [
            "uvicorn",
            "editor.backend.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "3839",
            "--reload",
        ]

        backend = subprocess.Popen(BACKEND_CMD)
        try:
            import webview

            webview.create_window("My Web App", "https://www.python.org")
            webview.start()
        except:
            webbrowser.open("0.0.0.0:3839")

        click.echo(f"Backend PID: {backend.pid}")

        try:
            backend.wait()
        except KeyboardInterrupt:
            click.echo("\nEncerrando...")
        finally:
            backend.terminate()
            backend.wait()
            click.echo("Finalizado.")


if __name__ == "__main__":
    from infra.init_db import init_db

    init_db()
    cli()
