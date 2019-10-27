#takes arguments and gives tracking info

import requests
import json
import sys

satid=sys.argv[1]
observer_lat=sys.argv[2]
observer_lng=sys.argv[3]
observer_alt=sys.argv[4]


# Albany Oregon: Lat= 44.66351 Long= -123.105

response= requests.get("https://www.n2yo.com/rest/v1/satellite/radiopasses/"+satid+"/"+observer_lat+"/"+observer_lng+"/"+observer_alt+"/1/40/&apiKey=JWH8ZQ-G7HTPQ-KRBG9Q-47TP")

print(response.status_code)
def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, indent=4)
    print(text)

jprint(response.json())
