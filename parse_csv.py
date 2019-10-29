import csv
import json

def parse_csv():
    Beacons = []
    with open('./data/beacons.csv') as beacons:
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
                    pass
                elif letter == "\n":
                    Beacons.append(row)
                    strang = ""
                    row = []
                else:
                    strang += letter
        for b in Beacons:
            print(b)
