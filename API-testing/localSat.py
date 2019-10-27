#Now can take arguments from the command line so it can be used in another program
import sys
import requests
import json

observer_lat=sys.argv[1]
observer_lng=sys.argv[2]
observer_alt=sys.argv[3]
# Albany Oregon: Lat= 44.66351 Long= -123.105
print(observer_lat)
response= requests.get("https://www.n2yo.com/rest/v1/satellite/above/"+observer_lat+"/"+observer_lng+"/"+observer_alt+"/90/18/&apiKey=JWH8ZQ-G7HTPQ-KRBG9Q-47TP")

#print(response.status_code)

json_data=response.json()
#print(json_data['above'][0]['satname'])
for i in json_data['above']:
    print i['satname'],
    print i['satid']
