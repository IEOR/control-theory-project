import sendgrid
import os
from sendgrid.helpers.mail import *
import pyrebase
import pymongo
import datetime
import pprint
from twilio.rest import Client



def get_db():
	client = pymongo.MongoClient('mongodb://localhost:27017/')
	db = client.test_database
	# collection = db.test_collection
	return db
	# users = db.users


def add_user(name, email, features):
	user = {"name": name, "email": email, "features": features, "date": datetime.datetime.utcnow()}
	user_id = users.insert_one(user).inserted_id
	print(user_id)
	# pprint.pprint(users.find_one())

def update_features(email, new_features):
	myquery = { "email": email}
	newvalues = { "$set": { "features": new_features } }

	users.update_one(myquery, newvalues)

	for x in users.find():
  		print(x)


# update_features("mike@gmail.com", [1, 2, 3, 4, 5, 6, 7])


def send_email(from_address, to_address, subject, text):
	sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY')) #only works locally
	from_email = Email(from_address)
	to_email = Email(to_address)
	content = Content("text/plain", text)
	mail = Mail(from_email, subject, to_email, content)
	response = sg.client.mail.send.post(request_body=mail.get())
	print(response.status_code)
	print(response.body)
	print(response.headers)

def send_test_email():
	from_address = "test@testing.com"
	to_address = "pmakkar97@gmail.com"
	subject = "test"
	text = "test"

	send_email(from_address, to_address, subject, text)


def send_text(from_number, to_number, body):
	account_sid = 'ACff26b77b06fd2bd97795b331ef0d8d25'
	auth_token = os.environ.get('TWILIO_AUTH')
	client = Client(account_sid, auth_token)

	message = client.messages.create(
		body=body,
		from_=from_number,
		to=to_number
	)
	return message.sid

def send_test_text():
	print(send_text('+15623860475', '+14086246734', "Join Earth's mightiest heroes."))

send_test_text()







# add_user("John", "john@gmail.com")
# get_users()

