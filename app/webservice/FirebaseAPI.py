from firebase import firebase
from firebase.firebase import FirebaseAuthentication


class filebaseAPI:
    def __init__(self, key, mailbox):
        self.app = firebase.FirebaseApplication('https://summer-hackathon-84d96.firebaseio.com/', None)
        authentication = FirebaseAuthentication(key, mailbox, True, True)
        self.app.authentication = authentication
        self.token = authentication.get_user().firebase_auth_token
        print(self.token)

    def query(self, database_name, table_name):
        params = {"print": "pretty"}
        result = self.app.get_async(database_name, table_name, params)
        return result

    def insert(self, database_name, table_name, data, callback_func):
        self.app.put_async(database_name, table_name, data, callback=callback_func)


if __name__ == "__main__":
    app = filebaseAPI("oin3wrNHY1tBS9uj6EScGcdtwpZZhnT1KMt2XSX6", "wangzijian09@gmail.com")