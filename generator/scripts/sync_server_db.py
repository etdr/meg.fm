
import json
import requests
from dotenv import dotenv_values

config = dotenv_values()

user = config["SERVER_USERNAME"]
pw = config["SERVER_PASSWORD"]

def post_uuids(uuids):

	payload = json.dumps({"uuids": uuids})

	auth = (user, pw)

	response = requests.post(
		"",
		data=payload,
		auth=auth,
		headers={"Content-Type": "application/json"}
	)

	print(f"Status code: {response.status_code}")
	print(f"Response: {response.json()}")