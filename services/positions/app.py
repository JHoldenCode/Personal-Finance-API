from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import json
import requests
import os

# TODO - make pytests for helper methods

# example curl request
# curl -X POST http://127.0.0.1:5000/positions -H "Content-Type: application/json" -d @input_new_positions.json
# for an example of the JSON structure for the routes below, check out testing/test_positions_json_objects.py

# CONSTANTS
DECIMAL_PLACES = 3

# setup flask app
app = Flask(__name__)

# enable cross-origin resource sharing on all routes
CORS(app)

# Configure MySQL connection URI
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# structure for Positions Database in MySQL
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

def get_stock_price(ticker, position_data):
    price = None
    if 'price' not in position_data:
        # setup query to Polygon stock API, i.e.
        # https://api.polygon.io/v2/aggs/ticker/{stock_ticker}/prev?apiKey=
        polygon_api_key = os.getenv('POLYGON_API_KEY')
        polygon_api_prefix = 'https://api.polygon.io/v2/aggs/ticker/'
        submit_api_key = 'prev?apiKey=' + polygon_api_key
        polygon_endpoint = polygon_api_prefix + ticker + '/' + submit_api_key

        # execute API request
        response = requests.get(polygon_endpoint)
        data = response.json()

        # closing price from previous day
        price = data['results'][0]['c']
        if price:
            price = round(price, DECIMAL_PLACES)
    else:
        price = position_data['price']
    
    return price


# ROUTES

@app.route('/positions', methods=['GET'])
def get_positions():
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
    
@app.route('/positions', methods=['POST'])
def post_positions():
    # TODO - check whether ticker is valid
    try:
        input_positions = request.get_json()['positions']

        # update database session for each position in input
        for ticker, position_data in input_positions.items():
            existing_position = Positions.query.get(ticker)

            price = get_stock_price(ticker, position_data)

            # if a price was not found from the polygon API do not modify database
            if not price:
                continue

            # update existing position or create new position
            if existing_position:
                existing_position.shares = position_data['shares']
                existing_position.cost_basis = position_data['cost_basis']
                existing_position.price = price
            else:
                new_position = Positions(
                    ticker = ticker,
                    shares = position_data['shares'],
                    cost_basis = position_data['cost_basis'],
                    price = price
                )
                db.session.add(new_position)
        
        db.session.commit()

        return 'Successfully updated positions relation with the new position data', 200
    except Exception as e:
        return f'Error: {str(e)}', 500

@app.route('/positions', methods=['DELETE'])
def delete_positions():
    # access positions submitted to endpoint
    positions_to_delete = request.get_json()['positions']

    # get positions from database that are in positions_to_delete
    positions_to_delete_query = Positions.query.filter(Positions.ticker.in_(positions_to_delete)).all()

    for position in positions_to_delete_query:
        db.session.delete(position)

    db.session.commit()

    return 'Successfully deleted from positions database.', 200

@app.route('/positions/clear_all', methods=['DELETE'])
def clear_all_positions():
    try:
        all_positions = Positions.query.all()

        for position in all_positions:
            db.session.delete(position)

        db.session.commit()

        return 'Successfully cleared all positions from the database.', 200
    except Exception as e:
        return f'Error: {str(e)}', 500


if __name__ == '__main__':
    # Create tables if they don't exist
    db.create_all()
    app.run(debug=True)