

#ROUTES FOR PYTHON TO GRAB

PORT = "8080"
ODS_PROTOCOL="https://"
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

CRED_OAUTH_REGISTERV2 = "/api/oauth"
CRED_ACCOUNT_GETV2 = "/endpoint-cred/{userId}/{type}"
CRED_ACCOUNTID_GETV2 = "/endpoint-cred/{userId}/{type}/{accountId}"
