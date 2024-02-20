from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import json
import requests
import os
from dotenv import load_dotenv

# example curl request
# curl -X POST http://127.0.0.1:5000/holdings -H "Content-Type: application/json" -d @input_new_holdings.json

# CONSTANTS

DECIMAL_PLACES = 3

app = Flask(__name__)
load_dotenv()

# enable cross-origin resource sharing on all routes
CORS(app)

# Configure MySQL connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# DB_FILE_PATH = 'databases/current_holdings.json'

# structure for Holdings Database in MySQL
class Positions(db.Model):
    __tablename__ = 'positions'
    ticker = db.Column(db.String(5), primary_key=True)
    shares = db.Column(db.Double, nullable=False)
    cost_basis = db.Column(db.Double, nullable=False)
    price = db.Column(db.Double, nullable=False)


# HELPER METHODS

def calculate_equity(price, shares):
    return round(price * shares, DECIMAL_PLACES)

def calculate_dollar_gain(price, cost_basis, shares):
    dollar_gain_per_share = price - cost_basis
    total_dollar_gain = dollar_gain_per_share * shares
    return round(total_dollar_gain, DECIMAL_PLACES)

def calcluate_percent_gain(price, cost_basis):
    # invalid cost_basis value
    if cost_basis <= 0:
        return 0
    dollar_gain_per_share = price - cost_basis
    percent_gain = dollar_gain_per_share / cost_basis * 100
    return round(percent_gain, DECIMAL_PLACES)

def calculate_total_percent_gain(total_equity, principal):
    # invalid principal
    if principal == 0:
        return 0
    growth_factor = total_equity / principal
    return round(growth_factor - 1, 3)

def convert_relation_to_json(json_obj, relation):
    total_equity = 0
    total_dollar_gain = 0
    # convert SQL table data on positions into json objects
    for position in relation:
        price = position.price
        cost_basis = position.cost_basis
        shares = position.shares
        ticker = position.ticker

        equity = calculate_equity(price, shares)
        dollar_gain = calculate_dollar_gain(price, cost_basis, shares)
        percent_gain = calcluate_percent_gain(price, cost_basis)

        # create position data object
        position_data = {
            'price': price,
            'cost_basis': cost_basis,
            'shares': shares,
            'equity': equity,
            'dollar_gain': dollar_gain,
            'percent_gain': percent_gain
        }
        json_obj['positions'][ticker] = position_data

        # increment sums of equity and dollar_gain
        total_equity += equity
        total_dollar_gain += dollar_gain

    return round(total_equity, DECIMAL_PLACES), round(total_dollar_gain, DECIMAL_PLACES)


@app.route('/positions', methods=['POST'])
def post_holdings():





    # # TODO - check whether ticker is valid
    # polygon_api_key = os.getenv('POLYGON_API_KEY')

    # # access holdings submitted to endpoint
    # new_holdings = request.get_json()['holdings']

    # # update and add from new holdings
    # current_holdings_json = {}
    # with open(DB_FILE_PATH, 'r') as db:
    #     # get view of current_holdings
    #     current_holdings_json = json.load(db)
    # current_holdings = current_holdings_json['holdings']

    # # setup query to Polygon stock API, i.e.
    # # https://api.polygon.io/v2/aggs/ticker/{stock_ticker}/prev?apiKey=
    # polygon_api_prefix = 'https://api.polygon.io/v2/aggs/ticker/'
    # submit_api_key = 'prev?apiKey=' + polygon_api_key

    # for new_holding in new_holdings:
    #     nh = new_holdings[new_holding]
    #     price = None

    #     # if new holding does not contain price, fetch stock price
    #     if 'price' not in nh:
    #         polygon_endpoint = polygon_api_prefix + new_holding + '/' + submit_api_key
    #         response = requests.get(polygon_endpoint)
    #         data = response.json()
            
    #         # closing price from previous day
    #         price = data['results'][0]['c']

    #         # if the fetched price is invalid, do not modify db according to this holding
    #         if not price:
    #             continue
    #         nh['price'] = round(price, 3)

    #     # update current holding with new data
    #     if new_holding in current_holdings:
    #         ch = current_holdings[new_holding]
    #         nh = new_holdings[new_holding]
    #         ch['price'] = nh['price']
    #         ch['shares'] = nh['shares']
    #         ch['cost_basis'] = nh['cost_basis']
    #     else: # add new holding data
    #         current_holdings[new_holding] = new_holdings[new_holding]

    #     with open(DB_FILE_PATH, 'w') as db:
    #         # Write the updated data back to the file
    #         json.dump(current_holdings_json, db, indent=4)

    # return 'Successfully updated holdings database with new holdings.', 200

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

@app.route('/positions', methods=['GET'])
def get_holdings_info():
    # query all positions from the database
    all_positions = Positions.query.all()

    # setup json object to be returned
    return_json = { 'positions': {}, 'compiled_stats': {} }

    # convert objects from sql relation into json objects
    # gather data on compiled stats
    total_equity, total_dollar_gain = convert_relation_to_json(return_json, all_positions)

    principal = total_equity - total_dollar_gain
    total_percent_gain = calculate_total_percent_gain(total_equity, principal)

    return_json['compiled_stats'] = {
        'total_equity': total_equity,
        'total_dollar_gain': total_dollar_gain,
        'total_percent_gain': total_percent_gain
    }

    return jsonify(return_json), 200


if __name__ == '__main__':
    # Create tables if they don't exist
    db.create_all()
    app.run(debug=True)