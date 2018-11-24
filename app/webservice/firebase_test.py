from firebase import firebase
from firebase.firebase import FirebaseAuthentication

app = firebase.FirebaseApplication('https://summer-hackathon-84d96.firebaseio.com/', None)


authentication = FirebaseAuthentication("yourkey", "youremail", True, True)
app.authentication = authentication

user = authentication.get_user()

result = app.get('/users', None, params={'print': 'pretty'})

print(result)

data={"abc":"def", "agg": 2}
