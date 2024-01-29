import requests
import json

# Replace the following URL with the actual URL of your Flask app
flask_endpoint_url = 'http://127.0.0.1:5000/update_holdings'

# Read the contents of the new_holdings.json file
with open('new_holdings_data.json', 'r') as file:
    data = json.load(file)

print(data)

# Convert the data to JSON
json_data = json.dumps(data)

# Set the headers for the request
headers = {"Content-Type": "application/json"}

# Send the POST request to the Flask endpoint
response = requests.post(flask_endpoint_url, data=json_data, headers=headers)

# Print the response
print(response.status_code)
print(response.text)
