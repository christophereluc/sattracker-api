from flask import Flask
from flask import request
from flask_mysqldb import MySQL
import requests
import json

import os

API_KEY = 'JWH8ZQ-G7HTPQ-KRBG9Q-47TP'
BASE_URL = "https://www.n2yo.com/rest/v1/satellite/"

app = Flask(__name__)

# set up mysql database
"""app.config['MYSQL_HOST'] = 'us-cdbr-iron-east-05.cleardb.net'
app.config['MYSQL_USER'] = os.environ["HAM_DATABASE_USER"]
app.config['MYSQL_PASSWORD'] = os.environ["HAM_DATABASE_PASSWORD"]
app.config['MYSQL_DB'] = 'heroku_95aba217f91d579'

mysql = MySQL(app)
"""

@app.route('/')
def hello_world():
    return 'Hello, World!'

#Usage: http://127.0.0.1:5000/nearby?lat=33.865990&lng=-118.175630&&alt=0
@app.route('/nearby')
def get_nearby_satellites():
    try:
        latitude = float(request.args.get('lat'))
        longitude = float(request.args.get('lng'))
        altitude = float(request.args.get('alt'))

        satellites = requests.get(
            BASE_URL + "above/" + str(latitude) + "/" + str(longitude) + "/" + str(altitude) + "/90/18/&apiKey=" + API_KEY).json()
        iss = requests.get(
            BASE_URL + "above/" + str(latitude) + "/" + str(longitude) + "/" + str(altitude) + "/90/2/&apiKey=" + API_KEY).json()

        satellites["above"] += iss["above"]

        return str(satellites["above"])

    except Exception as e:
        print("Unexpected error:", e)
        return "{ \"error\" : \"Unexpected error.  Ensure that contains lat/lng/alt parameters\"}"
#test_URLs: http://127.0.0.1:5000/tracking?id=13002&lat=33.865990&lng=-118.175630&&alt=0
@app.route('/tracking')
def get_tracking_info():
    try:
        satid = float(request.args.get('id'))
        latitude = float(request.args.get('lat'))
        longitude = float(request.args.get('lng'))
        altitude = float(request.args.get('alt'))

        satellites = requests.get(
                BASE_URL + "radiopasses/" + str(satid) + "/" + str(latitude) + "/" + str(longitude) + "/" + str(altitude) + "/2/10/&apiKey=" + API_KEY).json()
        return str(satellites)
    except Exception as e:
        print("Unexpected error:", e)
        return "{ \"error\" : \"Unexpected error.  Ensure that contains id/lat/lng/alt parameters\"}"
            
if __name__ == '__main__':
    app.run()

"""
response= requests.get("https://www.n2yo.com/rest/v1/satellite/radiopasses/"+satid+"/"+observer_lat+"/"+observer_lng+"/"+observer_alt+"/1/40/&apiKey=JWH8ZQ-G7HTPQ-KRBG9Q-47TP")

print(response.status_code)
def jprint(obj):
        # create a formatted string of the Python JSON object
            text = json.dumps(obj, indent=4)
                print(text)

                jprint(response.json())"""
