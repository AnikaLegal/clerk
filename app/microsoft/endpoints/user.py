from .base import BaseEndpoint
from .helpers import generate_password

# Office E1 License SKU ID
# https://www.microsoft.com/en-au/microsoft-365/enterprise/office-365-e1
OFFICE_E1_LICENSE_SKU_ID = "18181a46-0d4e-45cd-891e-60aabd171b4e"


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
            "mailNickname": fname,
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
        Returns User object or None if User doesn't exist.
        """
        data = {
            # Do not remove fields or POST request might fail.
            "addLicenses": [{"skuId": OFFICE_E1_LICENSE_SKU_ID}],
            "removeLicenses": [],
        }

        return super().post(f"users/{userPrincipalName}/assignLicense", data)

    def get_license(self, userPrincipalName):
        """
        Get User's license details.
        Returns license object or None if User doesn't exist.
        """
        return super().get(f"users/{userPrincipalName}/licenseDetails")
