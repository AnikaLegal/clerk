from accounts.models import User


# (1) Create User
def create_ms_graph_user(user: User):
    """Check if user is in Anika's MS account, if not, create user, assign license, and add to group"""


def user_exists(email: str) -> bool:
    endpoint = BASE_URL + "users/" + email
    response = requests.get(endpoint, headers=self.headers, stream=False)
    return response.status_code < 300


def create_user(email, first_name, last_name) -> str:
    endpoint = BASE_URL + "users"
    password = generate_password(16)
    data = {
        "accountEnabled": True,
        "displayName": f"{first_name} {last_name}",
        "mailNickname": first_name,
        "userPrincipalName": email,
        "usageLocation": "AU",
        "passwordProfile": {
            "forceChangePasswordNextSignIn": True,
            "password": password,
        },
    }
    return requests.post(endpoint, headers=self.headers, json=data, stream=False)


# (2) Assign E1 License

# (3) Add User to Group

# (4) Make copy of folder

# (5) Modify permissions on folder

# (6) Various GET requests
