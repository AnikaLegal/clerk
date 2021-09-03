from microsoft.base import BaseEndpoint
from microsoft.helpers import generate_password


class UserEndpoint(BaseEndpoint):
    """
    Endpoint for User.
    https://docs.microsoft.com/en-us/graph/api/resources/user
    """

    def get(self, userPrincipalName):
        """
        Get a User with their userPrincipalName (email).
        Returns User object or None.
        """
        return super().get(f"users/{userPrincipalName}")

    def create(self, fname, lname, userPrincipalName):
        """
        Creates a new User.
        Returns User object or raises HTTPError.
        """
        data = {
            # Do not alter fields or request might fail.
            "accountEnabled": True,
            "displayName": f"{fname} {lname}",
            "mailNickname": fname,
            "userPrincipalName": userPrincipalName,
            "usageLocation": "AU",
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": generate_password(),
            },
        }

        return super().post("users", data)

    def assign_license(self, userPrincipalName):
        """
        Assigns Office 365 E1 license to User.
        Returns User object or None if User doesn't exit.
        """
        data = {
            # Do not alter fields or request might fail.
            "addLicenses": [{"skuId": "18181a46-0d4e-45cd-891e-60aabd171b4e"}],
            "removeLicenses": [],
        }

        return super().post(f"users/{userPrincipalName}/assignLicense", data)

    def get_license(self, userPrincipalName):
        """
        Get User's license details.
        Returns license object or None if User doesn't exist.
        """
        return super().get(f"users/{userPrincipalName}/licenseDetails")
