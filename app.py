from flask import Flask
from flask import request
from flask_mysqldb import MySQL
import requests
import csv # for parsing beacon data
import urllib.request # for downloading beacon csv
from parse_csv import parse_csv # helper function to turn beacon data into sql-friendly struct
from post_data import post_data # helper function to post beacon data using MySQL
import os
import json

API_KEY = 'JWH8ZQ-G7HTPQ-KRBG9Q-47TP'
BASE_URL = "https://www.n2yo.com/rest/v1/satellite/"

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
            BASE_URL + "above/" + str(latitude) + "/" + str(longitude) + "/" + str(altitude) + "/90/18/&apiKey=" + API_KEY).json()
        iss = requests.get(
            BASE_URL + "above/" + str(latitude) + "/" + str(longitude) + "/" + str(altitude) + "/90/2/&apiKey=" + API_KEY).json()

        satellites["above"] += iss["above"]
        data = {"data": satellites["above"]}
        return json.dumps(data)
    except Exception as e:
        print("Unexpected error:", e)
        return "{ \"error\" : \"Unexpected error.  Ensure that contains lat/lng/alt parameters\"}"

#test_URLs: http://127.0.0.1:5000/tracking?id=13002&lat=33.865990&lng=-118.175630&&alt=0
@app.route('/tracking') #This can be used for position
def get_tracking_info():
    try:
        satid = int(request.args.get('id'))
        latitude = float(request.args.get('lat'))
        longitude = float(request.args.get('lng'))
        altitude = float(request.args.get('alt'))

        satellites = requests.get(
                BASE_URL + "radiopasses/" + str(satid) + "/" + str(latitude) + "/" + str(longitude) + "/" + str(altitude) + "/2/10/&apiKey=" + API_KEY).json()

        data = {"data": satellites["passes"]}

        return json.dumps(data)
    except Exception as e:
        print("Unexpected error:", e)
        return "{ \"error\" : \"Unexpected error.  Ensure that contains id/lat/lng/alt parameters\"}"

@app.route('/update_beacons')
def get_beacon_information():
    # GET BEACON DATA
    # satellite list as provided by N2Y0
    beac_url = 'http://www.ne.jp/asahi/hamradio/je9pel/satslist.csv'
    req = urllib.request.Request(beac_url)
    try:
        resp = urllib.request.urlopen(beac_url)
        # write contents of download to data file
        data = resp.read()
        text = data.decode('utf-8')
        open('./data/beacons.csv', 'w').write(text)
        print( "beacon request successful")
    except urllib.error.URLError as e:
        print("Error opening beacon data url:", e.reason)
        return "{ \"error\": \"Unexpected error parsing csv data\" }"
    existing_data = 1

    # PARSE BEACON DATA
    try:
        csv_data = open('./data/beacons.csv', 'r')
        beacons = parse_csv(csv_data)
    except Exception as e:
        print("Error parsing csv data:", e)
        return "{ \"error\": \"Unexpected error parsing csv data\" }"

    # ADD DATA TO DATABASE
    try:
        post_data(mysql, beacons)
        data = { "data": beacons }
        return json.dumps(data)
    except Exception as e:
        print("Error posting csv data to database:", e)
        return "{ \"error\": \"Unexpected error posting csv data\" }"

    return "beacon data updated"

if __name__ == '__main__':
    app.run()
