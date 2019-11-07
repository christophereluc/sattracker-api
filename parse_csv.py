# parses open csv file of beacon data and returns a list of beacon dictionary objects
def parse_csv(csv_file):
    matrix = [] # initial list of lists for each line
    Beacons = [] # final object for list of dicts
    with csv_file as beacons:
        for line in beacons:
            line = str(line)
            row = []
            strang = ""
            for letter in line:
                if not letter:
                    break
                if letter == ";":
                    row.append(strang)
                    strang = ""
                elif letter == "\n":
                    if strang == "active":
                        row.append(strang)
                        matrix.append(row)
                    strang = ""
                    row = []
                else:
                    strang += letter
    for b in matrix:
        params = {
            '_name'     : b[0],
            '_id'       : b[1],
            '_uplink'   : b[2].rstrip(), # remove trailing whitespaces
            '_downlink' : b[3].rstrip(),
            '_beacon'   : b[4].rstrip(),
            '_mode'     : b[5],
            '_callsign' : b[6]
        }
        Beacons.append(params)
    return Beacons
