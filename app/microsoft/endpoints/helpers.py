import logging
import secrets
import string

import msal

logger = logging.getLogger(__name__)

# Define constants for making requests to Graph API.
BASE_URL = "https://graph.microsoft.com/v1.0/"

HTTP_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def create_client(client_id, authority_url, client_secret):
    """Authenticate our app with Azure Active Directory."""
    client = msal.ConfidentialClientApplication(
        client_id=client_id, authority=authority_url, client_credential=client_secret
    )
    return client


def get_token(client):
    """Get access token after authenticating our app."""
    # Begin by looking in token cache, first arg is for scopes,
    # because token is for app rather than user, second arg is None.
    result = client.acquire_token_silent(
        ["https://graph.microsoft.com/.default"], account=None
    )

    if not result:
        logger.debug("No suitable token exists in cache. Get new one from Azure AD")
        result = client.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )

    # If we can't get access token, see what went wrong, otherwise return it.
    if "access_token" not in result:
        logger.exception(f"{result['error_description']} - {result['correlation_id']}")
    else:
        return result["access_token"]


def generate_password():
    """
    Generate password of length 16 that meets complexity requirements.
    Must have at least one: uppercase letter, lowercase letter, and digit.
    """
    selection = string.ascii_letters + string.digits

    while True:
        password = "".join(secrets.choice(selection) for i in range(16))

        if (
            any(c.isupper() for c in password)
            and any(c.islower() for c in password)
            and any(c.isdigit() for c in password)
        ):
            break

    return password
