from firebase import firebase
from firebase.firebase import FirebaseAuthentication


class filebaseAPI:
    def __init__(self, key, mailbox):
        self.app = firebase.FirebaseApplication('https://summer-hackathon-84d96.firebaseio.com/', None)
        authentication = FirebaseAuthentication(key, mailbox, True, True)
        self.app.authentication = authentication

    def query(self, table_name, filter):


    def insert(self, database_name, table_name, data, callback_func):
        self.app.put_async(database_name, table_name, data, callback=callback_func)
