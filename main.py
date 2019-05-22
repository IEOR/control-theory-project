import sendgrid
import os
import random
from sendgrid.helpers.mail import *
import pyrebase
import pymongo
import datetime
import pprint
from twilio.rest import Client
from bson import ObjectId
from flask import Flask, render_template, request
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

def get_db():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client.test_database
    return db

def send_text(to_number, body):
    from_number = '+15623860475'
    account_sid = 'ACff26b77b06fd2bd97795b331ef0d8d25'
    auth_token = os.environ.get('TWILIO_AUTH')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=body,
        from_=from_number,
        to=to_number
    )
    return message.sid


def add_user(db, first_name, last_name, email, phone, target):
    user = {"first_name": first_name, "last_name": last_name, "email": email,"phone": "+1" + phone, "target": target, "time_added": datetime.datetime.utcnow(), "control_vectors": [], "states": []}
    user_id = db.users.insert_one(user).inserted_id
    return user_id


def add_control_vector(db, user_id, control_vector):
#     user = db.users.find_one({"_id" : user_id})
    db.users.update_one(
       { "_id": user_id },
       { "$push": { "control_vectors": control_vector } }
    )
    
def pop_control_vector(user_id):
    db.users.update_one( { "_id": user_id }, { "$pop": { "control_vectors": 1 } } )
    
def add_state(db, user_id, state):
    db.users.update_one(
       { "_id": user_id },
       { "$push": { "states": state } }
    )
    
def pop_state(user_id):
    db.users.update_one( { "_id": user_id }, { "$pop": { "state": 1 } } )

      


def get_users():
    return db.users.find()


@app.route('/')
def home():
   return render_template('home.html')


@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      db = get_db()
      target = random.randint(1,101)
      add_user(db, result['first'], result['last'], result['email'], result['phone'], target)
      
      send_text(result['phone'], "Welcome " + result['first'] + "! Your target number is " + str(target) + ". Send me your current number")
      return render_template("result.html",result = result)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming messages and update user info."""

    from_number = request.form['From']
    to_number = request.form['To']
    body = request.form['Body']
    curr = int(body)
    db = get_db()
    user_id = db.users.find_one({"phone":from_number})['_id']
    target = db.users.find_one({"phone":from_number})['target']
    add_state(db, user_id, [curr, target])

    resp = MessagingResponse()


    if curr < target:
        step = "Increase"
    elif curr == target:
        step = "You're done!"
    else:
        step = "Decrease"

    add_control_vector(db, user_id, [step, target])


    resp.message(step)

    return str(resp)


if __name__ == '__main__':
   app.run(debug = True)



