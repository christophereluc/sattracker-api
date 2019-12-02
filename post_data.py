import pprint  # prettyprint for logging SQL params
from time import time


# INSERT or UPDATE sanitized parsed beacon data over the mysql connection to ClearDB database
def post_data(mysql, beacons):
    # open db connection
    cur = mysql.connection.cursor()
    # insert statement
    ins_str = '''
        INSERT INTO satellites
        (satid, name, uplink, downlink, beacon, mode, callsign, active)
        VALUES (
            %(_satid)s,
            %(_name)s,
            %(_uplink)s,
            %(_downlink)s,
            %(_beacon)s,
            %(_mode)s,
            %(_callsign)s ),
            %(_active)s'''
    # update statement
    upd_str = '''
        UPDATE satellites
        SET
        name=%(_name)s,
        uplink=%(_uplink)s,
        downlink=%(_downlink)s,
        beacon=%(_beacon)s,
        mode=%(_mode)s,
        callsign=%(_callsign)s,
        active=%(_active)s
        WHERE satid=%(_satid)s'''

    for beacon in beacons:
        # insert data if possible...
        try:
            cur.execute(ins_str, beacon)
            mysql.connection.commit()
            print("successfully inserted params " + pprint.pformat(beacon) + "into table 'satellites'")
        # ...otherwise, update
        except Exception as e:
            cur.execute(upd_str, beacon)
            mysql.connection.commit()
            print("successfully updated params " + pprint.pformat(beacon) + "into table 'satellites'")
    return 1


def post_nearby(mysql, lat, lng, alt, data, ttl):
    # open db connection
    cur = mysql.connection.cursor()
    # insert statement
    ins_str = '''
        INSERT INTO nearby
        (lat, lng, alt, data, ttl)
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s)'''
    try:
        items = (lat, lng, alt, data, ttl)
        cur.execute(ins_str, items)
        mysql.connection.commit()

    except Exception as e:
        print(e)
    return 1


def delete_nearby(mysql, lat, lng, alt):
    # open db connection
    cur = mysql.connection.cursor()
    # insert statement
    statement = '''DELETE FROM nearby WHERE alt = %s AND lat = %s AND lng = %s'''
    items = (alt, lat, lng)

    try:
        cur.execute(statement, items)
        mysql.connection.commit()
        print(cur.rowcount, "record(s) deleted")
    except Exception as e:
        print(e)
    return 1
