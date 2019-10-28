from flask import Flask
from flask import request
from flask_mysqldb import MySQL
import requests
import json
import urllib.request # for downloading beacon csv

import os

API_KEY = 'JWH8ZQ-G7HTPQ-KRBG9Q-47TP'
BASE_URL = "https://www.n2yo.com/rest/v1/satellite/above/"

app = Flask(__name__)

# set up mysql database
app.config['MYSQL_HOST'] = 'us-cdbr-iron-east-05.cleardb.net'
app.config['MYSQL_USER'] = os.environ["HAM_DATABASE_USER"]
app.config['MYSQL_PASSWORD'] = os.environ["HAM_DATABASE_PASSWORD"]
app.config['MYSQL_DB'] = 'heroku_95aba217f91d579'

mysql = MySQL(app)


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
            BASE_URL + str(latitude) + "/" + str(longitude) + "/" + str(altitude) + "/90/18/&apiKey=" + API_KEY).json()
        iss = requests.get(
            BASE_URL + str(latitude) + "/" + str(longitude) + "/" + str(altitude) + "/90/2/&apiKey=" + API_KEY).json()

        satellites["above"] += iss["above"]

        return str(satellites["above"])
    except Exception as e:
        print("Unexpected error:", e)
        return "{ \"error\" : \"Unexpected error.  Ensure that contains lat/lng/alt parameters\"}"


@app.route('/update_beacons')
def get_beacon_information():
    try:
        # satellite list as provided by N2Y0
        beac_url = 'http://www.ne.jp/asahi/hamradio/je9pel/satslist.csv'
        resp = urllib.request.urlopen(beac_url)
        # write contents of download to data file
        data = resp.read()
        text = data.decode('utf-8')
        open('./data/beacons.csv', 'w').write(text)
        return 1
    except Exception as e:
        print("unexpected error:", e)
        return "{ \"error\" : \"Could not connect to either beacon data or SQL database. Try again later.\"}"
if __name__ == '__main__':
    app.run()
