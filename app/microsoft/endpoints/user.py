from .base import BaseEndpoint
from .helpers import generate_password

# See https://learn.microsoft.com/en-us/entra/identity/users/licensing-service-plan-reference
MS_OFFICE_LICENSE_SKU_ID = (
    "3b555118-da6a-4418-894f-7df1e2096870"  # Microsoft 365 Business Basic plan
)


class UserEndpoint(BaseEndpoint):
    """
    Endpoint for User.
    https://docs.microsoft.com/en-us/graph/api/resources/user
    """

    def get(self, userPrincipalName):
        """
        Get User through their userPrincipalName (usually email).
        Returns User object or None.
        """
        return super().get(f"users/{userPrincipalName}")

    def create(self, fname, lname, userPrincipalName):
        """
        Create new User.
        Returns User object and password, or raises HTTPError.
        """
        password = generate_password()

        data = {
            # Do not remove fields or POST request might fail.
            "accountEnabled": True,
            "displayName": f"{fname} {lname}",
            "mailNickname": fname.split(" ")[0],
            "userPrincipalName": userPrincipalName,
            "usageLocation": "AU",
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": password,
            },
        }

        user = super().post("users", data)

        return user, password

    def assign_license(self, userPrincipalName):
        """
        Assign Office 365 E1 license to User.
        """
        data = {
            # Do not remove fields or POST request might fail.
            "addLicenses": [{"skuId": MS_OFFICE_LICENSE_SKU_ID}],
            "removeLicenses": [],
        }
        return super().post(f"users/{userPrincipalName}/assignLicense", data)

    def remove_license(self, userPrincipalName):
        """
        Removes Office 365 E1 license from User.
        """
        data = {
            # Do not remove fields or POST request might fail.
            "addLicenses": [],
            "removeLicenses": [MS_OFFICE_LICENSE_SKU_ID],
        }
        return super().post(f"users/{userPrincipalName}/assignLicense", data)

    def get_license(self, userPrincipalName):
        """
        Get User's license details.
        Returns license object or None if User doesn't exist.
        """
        return super().get(f"users/{userPrincipalName}/licenseDetails")
