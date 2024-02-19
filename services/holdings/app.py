from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import requests
import os
from dotenv import load_dotenv

# example curl request
# curl -X POST http://127.0.0.1:5000/holdings -H "Content-Type: application/json" -d @input_new_holdings.json

app = Flask(__name__)

# enable cross-origin resource sharing on all routes
CORS(app)

DB_FILE_PATH = 'databases/current_holdings.json'

@app.route('/holdings', methods=['POST'])
def post_holdings():
    # TODO - check whether ticker is valid
    load_dotenv()
    polygon_api_key = os.getenv('POLYGON_API_KEY')

    # access holdings submitted to endpoint
    new_holdings = request.get_json()['holdings']

    # update and add from new holdings
    current_holdings_json = {}
    with open(DB_FILE_PATH, 'r') as db:
        # get view of current_holdings
        current_holdings_json = json.load(db)
    current_holdings = current_holdings_json['holdings']

    # setup query to Polygon stock API, i.e.
    # https://api.polygon.io/v2/aggs/ticker/{stock_ticker}/prev?apiKey=
    polygon_api_prefix = 'https://api.polygon.io/v2/aggs/ticker/'
    submit_api_key = 'prev?apiKey=' + polygon_api_key

    for new_holding in new_holdings:
        nh = new_holdings[new_holding]
        price = None

        # if new holding does not contain price, fetch stock price
        if 'price' not in nh:
            polygon_endpoint = polygon_api_prefix + new_holding + '/' + submit_api_key
            response = requests.get(polygon_endpoint)
            data = response.json()
            
            # closing price from previous day
            price = data['results'][0]['c']

            # if the fetched price is invalid, do not modify db according to this holding
            if not price:
                continue
            nh['price'] = round(price, 3)

        # update current holding with new data
        if new_holding in current_holdings:
            ch = current_holdings[new_holding]
            nh = new_holdings[new_holding]
            ch['price'] = nh['price']
            ch['shares'] = nh['shares']
            ch['cost_basis'] = nh['cost_basis']
        else: # add new holding data
            current_holdings[new_holding] = new_holdings[new_holding]

        with open(DB_FILE_PATH, 'w') as db:
            # Write the updated data back to the file
            json.dump(current_holdings_json, db, indent=4)

    return 'Successfully updated holdings database with new holdings.', 200

@app.route('/holdings', methods=['DELETE'])
def delete_holdings():
    # access holdings submitted to endpoint
    holdings_to_delete = request.get_json()['holdings']

    # create new json obj that will be written to file
    modified_db = { "holdings": {}}
    # include only holdings that are not to be deleted in modified db
    with open(DB_FILE_PATH, 'r') as db:
        current_holdings = json.load(db)['holdings']
        modified_db['holdings'] = { obj: current_holdings[obj] for obj in current_holdings if obj not in holdings_to_delete }

    # overwrite file with new db json
    with open(DB_FILE_PATH, 'w') as db:
        json.dump(modified_db, db, indent=4)

    return "Successfully deleted from holdings database.", 200

@app.route('/holdings/clear_all', methods=['DELETE'])
def clear_all_holdings():
    modified_db = { 'holdings': {} }
    with open(DB_FILE_PATH, 'w') as db:
        json.dump(modified_db, db, indent=4)

    return "Successfully cleared all holdings from database.", 200

@app.route('/holdings', methods=['GET'])
def get_holdings_info():
    current_holdings_json = {}

    with open(DB_FILE_PATH, 'r') as db:
        current_holdings_json = json.load(db)

    current_holdings = current_holdings_json['holdings']
    total_equity = 0
    total_dollar_gain = 0
    for holding in current_holdings:
        holding_info = current_holdings[holding]

        # access holding info
        price = holding_info['price']
        shares = holding_info['shares']
        cost_basis = holding_info['cost_basis']

        # add new holding info fields
        equity = round(price * shares, 3)
        dollar_gain = round((price - cost_basis) * shares, 3)
        holding_info['equity'] = equity
        holding_info['dollar_gain'] = dollar_gain
        holding_info['percent_gain'] = round((price - cost_basis) / cost_basis * 100, 3) if cost_basis > 0 else 0

        # increment sums of equity and dollars gained
        total_equity += equity
        total_dollar_gain += dollar_gain
    
    # append separate JSON object of sums
    total_dollar_gain = round(total_dollar_gain, 3)
    principal = total_equity - total_dollar_gain
    total_percent_gain = round(total_equity / principal - 1, 3) if principal != 0 else 0
    current_holdings_json['compiled_stats'] = {
        'total_equity': total_equity,
        'total_dollar_gain': total_dollar_gain,
        'total_percent_gain': total_percent_gain
    }

    return current_holdings_json, 200


if __name__ == '__main__':
    app.run(debug=True)