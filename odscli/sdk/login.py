import click
import odscli.sdk.token_utils as token_utils
import os


@click.group('auth_cli')
@click.pass_context
def auth_cli():
    pass


@auth_cli.group('auth')
def auth():
    pass


@auth.command("login")
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
@click.option("--host", default="onedatashare.org")
def login(username, password, host):
    print(host)
    work, tok = token_utils.login(host=host, user=username, password=password)

    if work:
        print("\nSuccessfully Logged In!\n")
        return
    else:
        print(
            "\nProblem Logging In try signing in on https://onedatashare.org to make sure your credentials are accurate\n")

@auth.command("logout")
def logout():
    token_utils.logout()
    print("Successfully logged out")