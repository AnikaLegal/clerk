from firebase import firebase
from firebase.firebase import FirebaseAuthentication


class filebaseAPI:
    def __init__(self, key, mailbox):
        self.app = firebase.FirebaseApplication('https://summer-hackathon-84d96.firebaseio.com/', None)
        authentication = FirebaseAuthentication(key, mailbox, True, True)
        self.app.authentication = authentication
        self.token = authentication.get_user().firebase_auth_token
        # print(self.token)

    def query(self, database_name, table_name):
        params = {"print": "pretty"}
        result = self.app.get(database_name, name=table_name, params=params)
        return result

    def insert(self, database_name, table_name, data):
        if isinstance(data, list):
            for item in data:
                self.app.post(database_name + "/" + table_name, item)
        else:
            self.app.post(database_name + "/" + table_name, data)


if __name__ == "__main__":
    app = filebaseAPI("oin3wrNHY1tBS9uj6EScGcdtwpZZhnT1KMt2XSX6", "wangzijian09@gmail.com")
    print(app.query('/tests', "specs"))