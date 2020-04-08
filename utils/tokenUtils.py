import os


def get_ods_auth_token() -> str:
    token = os.environ['ODS_AUTH_TOKEN']
    if token is None:
        raise LookupError("ODS auth token not found")
    return token