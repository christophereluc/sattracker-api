from flask import Flask
from flask import request
from flask_mysqldb import MySQL
from time import time
import requests
import csv  # for parsing beacon data
import urllib.request  # for downloading beacon csv
from parse_csv import parse_csv  # helper function to turn beacon data into sql-friendly struct
from post_data import post_data  # helper function to post beacon data using MySQL
from post_data import post_nearby
from post_data import delete_nearby
from json_serialize import json_serialize  # helper function to return mysql as json_serialize
import os
import json

API_KEY = 'JWH8ZQ-G7HTPQ-KRBG9Q-47TP'
BASE_URL = "https://www.n2yo.com/rest/v1/satellite/"
ROUNDING_VALUE = 3
TTL = 2 * 60  # time in seconds

app = Flask(__name__)

# set up mysql database
app.config['MYSQL_HOST'] = 'us-cdbr-iron-east-05.cleardb.net'
app.config['MYSQL_USER'] = os.environ["HAM_DATABASE_USER"]
app.config['MYSQL_PASSWORD'] = os.environ["HAM_DATABASE_PASSWORD"]
app.config['MYSQL_DB'] = 'heroku_95aba217f91d579'

mysql = MySQL(app)


# Function used to round a value based on ROUNDING_VALUE
# i.e. truncate to 3 decimal places
def roundPosition(value):
    return round(value, ROUNDING_VALUE)


# Usage: http://127.0.0.1:5000/nearby?lat=33.865990&lng=-118.175630&&alt=0
@app.route('/nearby')
def get_nearby_satellites():
    try:
        # truncate lat/long for easier caching for now
        latitude = roundPosition(float(request.args.get('lat')))
        longitude = roundPosition(float(request.args.get('lng')))
        altitude = float(request.args.get('alt'))

        # Query database and see if we already have an item where lat/lng/alt match
        cursor = mysql.connection.cursor()
        statement = '''SELECT data, ttl FROM nearby WHERE alt = %s AND lat = %s AND lng = %s'''
        items = (altitude, latitude, longitude)

        cursor.execute(statement, items)
        row = cursor.fetchone()

        expired = False

        # If we found a row, check if its expired
        if row is not None:
            expired = row[1] <= time()

        # If no item was found or the ttl passed, we need to query api again
        if row is None or expired:
            satellites = requests.get(
                BASE_URL + "above/" + str(latitude) + "/" + str(longitude) + "/" + str(
                    altitude) + "/90/18/&apiKey=" + API_KEY).json()
            iss = requests.get(
                BASE_URL + "above/" + str(latitude) + "/" + str(longitude) + "/" + str(
                    altitude) + "/90/2/&apiKey=" + API_KEY).json()

            satellites["above"] += iss["above"]
            data = {"data": satellites["above"]}

            # Delete stale data
            if expired:
                delete_nearby(mysql, latitude, longitude, altitude)

            # Now post it to the cache
            post_nearby(mysql, latitude, longitude, altitude, json.dumps(data), (time() + TTL))

            # TODO and cache then return
            cursor.close()
            return json.dumps(data)

        cursor.close()
        return json.dumps(row[0])
    except Exception as e:
        print("Unexpected error:", e)
        return "{ \"error\" : \"Unexpected error.  Ensure that contains lat/lng/alt parameters\"}"


# test_URLs: http://127.0.0.1:5000/tracking?id=13002&lat=33.865990&lng=-118.175630&&alt=0
@app.route('/tracking')  # This can be used for position
def get_tracking_info():
    try:
        satid = int(request.args.get('id'))
        latitude = float(request.args.get('lat'))
        longitude = float(request.args.get('lng'))
        altitude = float(request.args.get('alt'))

        satellites = requests.get(
            BASE_URL + "radiopasses/" + str(satid) + "/" + str(latitude) + "/" + str(longitude) + "/" + str(
                altitude) + "/2/10/&apiKey=" + API_KEY).json()

        data = {"data": satellites["passes"]}

        return json.dumps(data)
    except Exception as e:
        print("Unexpected error:", e)
        return "{ \"error\" : \"Unexpected error.  Ensure that contains id/lat/lng/alt parameters\"}"

# test URL: http://127.0.0.1:5000/beacons?ids=[35935, 28895, 37855, 42766, 43678]
@app.route('/beacons')
def print_beacon_information():
    ids = request.args.get('id')[1:-1].split(', ')  # get query string
    # build up SQL query
    for i, id in enumerate(ids):
        # sanitize query
        try:
            satid = ids[i].strip()
            ids[i] = 'satid=' + satid
            print(satid)
        except Exception as e:
            print("invalid query string")
            return "{ \"error\": \"Invalid query format (should be /beacons?ids=[12345,67890])\" }"
    sql_ids = ' OR '.join(ids)
    dump_str = "SELECT * FROM satellites WHERE " + sql_ids + ";"
    # call SQL query
    try:
        cur = mysql.connection.cursor()
        cur.execute(dump_str)
        rows = cur.fetchall()
        result = json_serialize(rows, cur)
        print("successfully obtained beacon data from table 'satellites'")
        data = {"data" : result}
        return json.dumps(data)
    except Exception as e:
        print("unable to retrieve beacon data: " + e)
        return "{ \"error\" : \"Unexpected error fetching from database\"}"


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
        print("beacon request successful")
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
        data = {"data": beacons}
        return json.dumps(data)
    except Exception as e:
        print("Error posting csv data to database:", e)
        return "{ \"error\": \"Unexpected error posting csv data\" }"

    return "beacon data updated"


if __name__ == '__main__':
    app.run()
