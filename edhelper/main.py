"""
Entry point principal - apenas comandos básicos (shell, editor, version).
Comandos CLI completos estão em cli/
"""

import click
from edhelper.infra.config import settings
from edhelper.infra.init_db import init_db


@click.group(invoke_without_command=True)
@click.option("-v", "--version", is_flag=True, help="Show version.")
@click.option("--info", is_flag=True, help="Show metadata.")
@click.option("--get-key", is_flag=True)
@click.option(
    "--set-key",
    is_flag=True,
    help="Create and store API credentials using keyring.",
)
@click.option("--logout", is_flag=True)
@click.pass_context
def cli(ctx, version, info, get_key, set_key, logout):
    """edhelper — EDH deck builder & analyzer."""

    if version:
        click.echo(f"edhelper {settings.VERSION}")
        ctx.exit()

    if set_key:
        try:
            from edhelper.external.api import create_client

            click.echo("Creating new client credentials...")
            result = create_client()
            api_key = result.get("api_key") or result.get("apiKey")
            client_id = result.get("client_id") or result.get("clientId")

            if not api_key or not client_id:
                click.echo(f"Error: Unexpected response format: {result}", err=True)
                ctx.exit(1)

            settings.set_credentials(api_key, client_id)
            click.echo("Credentials stored successfully in keyring!")
            click.echo(f"Client ID: {client_id}")
        except Exception as e:
            click.echo(f"Error: {str(e)}", err=True)
            ctx.exit(1)
        ctx.exit()

    if logout:
        settings.clear_credentials()
        click.echo("Credentials cleared from keyring.")
        ctx.exit()

    if not settings.user_is_authenticated():
        click.echo("You need to authenticate first (--set-key).")
        ctx.exit()


@cli.command()
def shell():
    """Run a shell."""
    try:
        from edhelper.commom.utils import clear_screen
        from edhelper.shell.repl.repl import repl

        clear_screen()
        repl()
    except ImportError:
        click.echo(
            "Error: Shell functionality not available. Install with: pip install edhelper[shell]",
            err=True,
        )


@cli.command()
def start_editor():
    """Inicia o editor."""
    import sys
    import subprocess
    import webbrowser

    try:
        BACKEND_CMD = [
            sys.executable,
            "-m",
            "uvicorn",
            "edhelper.editor.backend.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "3839",
        ]

        backend = subprocess.Popen(BACKEND_CMD)

        webbrowser.open("http://0.0.0.0:3839")

        try:
            backend.wait()
        except KeyboardInterrupt:
            click.echo("\nEncerrando...")
        finally:
            backend.terminate()
            backend.wait()
            click.echo("Finalizado.")

    except ImportError:
        click.echo(
            "Error: Editor functionality not available. Install with: pip install edhelper[editor]",
            err=True,
        )


init_db()


if __name__ == "__main__":
    cli()
