import click
import sdk.token_utils as token_utils
import os


@click.group('login_cli')
@click.pass_context
def login_cli():
    pass


@login_cli.group('login')
def login():
    pass


@login.command("login")
@click.option(
    "--username", prompt=False,
    default=lambda: os.environ.get("ODS_CLI_USER"),
    help="Username (default: from ODS_CLI_USER environment variable)"
)
@click.option(
    "--password", prompt=False, hide_input=True,
    confirmation_prompt=True, default=lambda: os.environ.get("ODS_CLI_PWD"),
    help="Password (default: from ODS_CLI_PWD environment variable)"
)
@click.option("--host", default="https://onedatashare.org")
def login(user, password, host):
    work, tok = token_utils.login(host=host, user=user, password=password)

    if work:
        print("\nSuccessfully Logged In!\n")
        return
    else:
        print(
            "\nProblem Logging In try signing in on https://onedatashare.org to make sure your credentials are accurate\n")
