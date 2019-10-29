import pprint # prettyprint for logging SQL params

# INSERT or UPDATE sanitized parsed beacon data over the mysql connection to ClearDB database
def post_data(mysql, beacons):
    #open db connection
    cur = mysql.connection.cursor()
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

    for beacon in beacons:
        # insert data if possible...
        try:
            cur.execute(ins_str, beacon)
            mysql.connection.commit()
            print("successfully inserted params " + pprint.pformat(beacon) + "into table 'satellites'" )
        # ...otherwise, update
        except Exception as e:
            cur.execute(upd_str, beacon)
            mysql.connection.commit()
            print("successfully updated params " + pprint.pformat(beacon) + "into table 'satellites'" )
    return 1
