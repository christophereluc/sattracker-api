# parses open csv file of beacon data and returns a list of beacon dictionary objects
def parse_csv(csv_file):
    matrix = [] # initial list of lists for each line
    Beacons = [] # final object for list of dicts
    with csv_file as beacons:
        for line in beacons:
            line = str(line)
            # row = []
            strang = ""
            row = line.split(";")
            matrix.append(row)
            print(row)

    for b in matrix:
        active = 1 if b[7] == "active\n" else 0
        params = {
            '_name'     : b[0],
            '_satid'    : b[1],
            '_uplink'   : b[2].rstrip(), # remove trailing whitespaces
            '_downlink' : b[3].rstrip(),
            '_beacon'   : b[4].rstrip(),
            '_mode'     : b[5],
            '_callsign' : b[6],
            '_active'   : active
        }
        Beacons.append(params)
    return Beacons
