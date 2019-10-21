import requests
import json
#Returns all the satellites in a given degree radius. Hard coded GPS coordinates were added for this simple test.

# Albany Oregon: Lat= 44.66351 Long= -123.105

response= requests.get("https://www.n2yo.com/rest/v1/satellite/above/44.663/-123.105/0/30/18/&apiKey=JWH8ZQ-G7HTPQ-KRBG9Q-47TP")

print(response.status_code)
def jprint(obj):
        # create a formatted string of the Python JSON object
            text = json.dumps(obj, indent=4)
                print(text)
                jprint(response.json())
