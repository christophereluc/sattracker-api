from flask import Flask
from flask import request
from flask_mysqldb import MySQL
import requests
import json
import csv # for parsing beacon data
import urllib.request # for downloading beacon csv
from parse_csv import parse_csv # custom function to turn beacon data into sql-friendly struct
import pprint # prettyprint for logging SQL params
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
        print(e.reason)
        return 0
    existing_data = 1

    # PARSE BEACON DATA
    # each beacon in list [name, id, uplink, downlink, beacon, mode, callsign, status]
    # TODO: just instantiate as list of dictionaries instead of this vague matrix crap
    csv_data = open('./data/beacons.csv', 'r')
    beacons = parse_csv(csv_data)

    # ADD DATA TO DATABASE
    # insert statement
    ins_str = '''
        INSERT INTO satellites
        (id, name, uplink, downlink, beacon, mode, callsign)
        VALUES (
            %(_id)s,
            %(_name)s,
            %(_uplink)s,
            %(_downlink)s,
            %(_beacon)s,
            %(_mode)s,
            %(_callsign)s )'''
    # update statement
    upd_str = '''
        UPDATE satellites
        SET
        name=%(_name)s,
        uplink=%(_uplink)s,
        downlink=%(_downlink)s,
        beacon=%(_beacon)s,
        mode=%(_mode)s,
        callsign=%(_callsign)s
        WHERE id=%(_id)s'''
    #open db connection
    cur = mysql.connection.cursor()
    for b in beacons:
        # sanitized beacon data
        params = {
            '_name'     : b[0],
            '_id'       : b[1],
            '_uplink'   : b[2],
            '_downlink' : b[3],
            '_beacon'   : b[4],
            '_mode'     : b[5],
            '_callsign' : b[6]
        }
        # insert data if possible...
        try:
            cur.execute(ins_str, params)
            mysql.connection.commit()
            print("successfully inserted params " + pprint.pformat(params) + "into table 'satellites'" )
        # ...otherwise, update entry
        except Exception as e:
            cur.execute(upd_str, params)
            mysql.connection.commit()
            print("successfully updated params " + pprint.pformat(params) + "into table 'satellites'" )

    return "beacon data updated"
