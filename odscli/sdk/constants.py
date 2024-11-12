# ROUTES FOR PYTHON TO GRAB

PORT = "8080"
ODS_PROTOCOL = "https://"
LISTV1 = "/api/{type}/ls"
LISTV2 = "/api/{type}/ls"
MKDIRV1 = "/api/{type}/mkdir"
MKDIRV2 = "/api/{type}/mkdir"
REMOVEV2 = "/api/{type}/rm"
DOWNLOADV2 = "/api/{type}/download"
TRANSFER = "/api/transferjob"
VALIDATE_EMAILV1 = "/is-email-registered"
VALIDATE_EMAILV2 = "/is-email-registered"
AUTHENTICATEV1 = "/authenticate"
AUTHENTICATEV2 = "/authenticate"
CRED_ACCOUNT_REGISTERV2 = "/api/cred/{type}"
CRED_ACCOUNT_DELETE = "/api/cred/{type}/{credID}"
SCHEDULE = "/api/job"

CRED_OAUTH_REGISTERV2 = "/api/oauth"
CRED_ACCOUNT_GETV2 = "/endpoint-cred/{userId}/{type}"
CRED_ACCOUNTID_GETV2 = "/endpoint-cred/{userId}/{type}/{accountId}"

NODE_LIST_CONNECTORS = "/api/nodes/{user}"
NODE_LIST_ODS = "/api/nodes/ods"
NODE_COUNT = "/api/nodes/count"

CARBON_API = "/api/carbon"
CARBON_NODE_AND_JOB = "/query/{transferNodeName}/{jobUuid}"
CARBON_USER = "/user"
CARBON_JOB = "/job/{jobUuid}"
CARBON_NODE = "/node/{transferNodeName}"
CARBON_LATEST = "/latest/{jobUuid}"
CARBON_RESULT = "/result/{job_uuid}"


def human_readable_size(size_in_bytes):
    """Convert bytes to a human-readable string with appropriate units."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} PB"  # Handles very large sizes
