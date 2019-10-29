def parse_csv(csv_file):
    Beacons = []
    with csv_file as beacons:
        for line in beacons:
            line = str(line)
            row = []
            strang = ""
            for letter in line:
                if not letter:
                    print(Beacons)
                    break
                if letter == ";":
                    row.append(strang)
                    strang = ""
                elif letter == "\n":
                    if strang == "active":
                        row.append(strang)
                        Beacons.append(row)
                    strang = ""
                    row = []
                else:
                    strang += letter
    return Beacons
