import json

from firebase import firebase
from firebase.firebase import FirebaseAuthentication

app = firebase.FirebaseApplication('https://summer-hackathon-84d96.firebaseio.com/', None)


authentication = FirebaseAuthentication("oin3wrNHY1tBS9uj6EScGcdtwpZZhnT1KMt2XSX6", "wangzijian09@gmail.com", True, True)
app.authentication = authentication

user = authentication.get_user()

result = app.get('/tests', name="specs", params={"print": "pretty"})
print("test")
print(result)

# input_file = open('rules.json')
# # input_file = open('../../spec/spec-example.json')
# json_array = json.load(input_file)
# print(json_array)

# data={"abc":"def", "agg": 2}
#
# app.put("/", "rules", json_array)
