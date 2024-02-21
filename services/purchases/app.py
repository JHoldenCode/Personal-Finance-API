from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
import json
import os

# example curl request
# curl -X POST http://127.0.0.1:5001/purchases -H "Content-Type: application/json" -d @input_post_purchases.json
# for an example of the JSON structure for the routes below, check out testing/test_purchase_json_objects.py

# CONSTANTS

# setup flask app
app = Flask(__name__)

# enable cross-origin resource sharing on all routes
CORS(app)

# configure MySQL connection URI
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize SQLAlchemy
db = SQLAlchemy(app)

# structure for Purchases database in MySQL
class Purchases(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Double, nullable=False)
    memo = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)

# HELPER METHODS

def transfer_purchases_from_json(return_purchases, current_purchases, date):
    month, day, year = date.split('/')
    if year not in return_purchases:
        return_purchases[year] = {}

    if month not in return_purchases[year]:
        return_purchases[year][month] = {}

    return_purchases[year][month][date] = current_purchases[year][month][date]

def convert_relation_to_json(relation, json_obj):
    for purchase in relation:
        purchase_data = {
            'id': purchase.id,
            'date': purchase.date,
            'amount': purchase.amount,
            'memo': purchase.memo,
            'category': purchase.category
        }

        json_obj['purchases'].append(purchase_data)

def validate_date_arguments(start_date, end_date):
    NO_ARG_MSG = "Must submit a start and/or end date for this endpoint using the args 'start' and 'end'.\nUse the /money_spent/all_purchases endpoint to get all purchase records."

    if not start_date and not end_date:
        raise ValueError(NO_ARG_MSG)

    if not start_date:
        # set arbitrary start date from long ago to include purchases up until end_date
        start_date = '9/15/1215'
    if not end_date:
        # set arbitrary end date far in future to include purchases after start date
        end_date = '1/24/5090'

    return start_date, end_date

def verify_chronological_order(start_date, end_date):
    NOT_CHRONO_MSG = 'Unable to retrieve purchases in a range where start date is after end date.'

    # check that end date is after or on same day as start date
    start_date_timestamp = datetime.strptime(start_date, '%m/%d/%Y')
    end_date_timestamp = datetime.strptime(end_date, '%m/%d/%Y')
    if start_date_timestamp > end_date_timestamp:
        raise ValueError(NOT_CHRONO_MSG)
    
    return start_date_timestamp, end_date_timestamp

# returns a list of tuples of the sum of all purchases in each category (category, sum)
def category_summation_query(start_date_timestamp, end_date_timestamp):
    query = db.session.query(Purchases.category, func.sum(Purchases.amount).label('total_amount')) \
        .filter(Purchases.date.between(start_date_timestamp, end_date_timestamp)) \
        .group_by(Purchases.category).all()
    return query

def delete_purchases_from_date(current_purchases, date, indices_to_delete):
    # try to find date obj in current purchases json
    month, day, year = date.split('/')
    purchases_on_date = {}
    try:
        purchases_on_date = current_purchases[year][month][date]
    except KeyError:
        return
    
    modified_purchases_on_date = []
    for i, purchase in enumerate(purchases_on_date):
        if i not in indices_to_delete:
            modified_purchases_on_date.append(purchase)
    
    current_purchases[year][month][date] = modified_purchases_on_date
    

# ROUTES

# returns whole DB file
@app.route('/purchases/all_purchases', methods=['GET'])
def get_all_purchases():
    all_purchases = Purchases.query.all()

    return_json = { 'purchases': [] }
    convert_relation_to_json(all_purchases, return_json)

    return jsonify(return_json), 200

# arguments: start, end -> str in MM/DD/YYYY format
@app.route('/purchases/range', methods=['GET'])
def get_range_of_purchases():
    # get arguments for start and end dates inclusive
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    try:
        start_date, end_date = validate_date_arguments(start_date, end_date)
        start_date_timestamp, end_date_timestamp = verify_chronological_order(start_date, end_date)
    except ValueError as err:
        return str(err), 400

    return_json = { 'purchases': [] }
    purchases_in_date_range = Purchases.query.filter(Purchases.date.between(start_date_timestamp, end_date_timestamp)).all()

    convert_relation_to_json(purchases_in_date_range, return_json)

    return jsonify(return_json), 200

# arguments: start, end -> str in MM/DD/YYYY format
@app.route('/purchases/category_summation', methods=['GET'])
def get_category_summation():
    # get arguments for start and end dates inclusive
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    try:
        start_date, end_date = validate_date_arguments(start_date, end_date)
        start_date_timestamp, end_date_timestamp = verify_chronological_order(start_date, end_date)
    except ValueError as err:
        return str(err), 400

    return_json = { 'categories': {} }

    # gets the sum of all purchases in each category returned as a list of tuples
    category_summation = category_summation_query(start_date_timestamp, end_date_timestamp)
    for category, amount in category_summation:
        return_json['categories'][category] = amount

    return_json['date_range'] = {
        'start_date': start_date,
        'end_date': end_date
    }

    return jsonify(return_json), 200

@app.route('/money_spent', methods=['POST'])
def post_money_spent():
    # access purchases submitted to endpoint
    new_purchase_dates = request.get_json()['purchases']

    # update and add from new purchases
    with open(DB_FILE_PATH, 'r+') as db:
        # get view of current purchases
        current_purchases_json = json.load(db)
        current_purchases = current_purchases_json['purchases']

        # move cursor to top so file write begins at correct spot
        # do not need to delete all contents because new file will be at
        # least as long as old file
        db.seek(0)

        for new_purchase_date in new_purchase_dates:
            # TODO - ensure date is in MM-DD-YYYY format
            month, day, year = new_purchase_date.split('/')

            # if year from new purchase never seen before, add empty month object for every month in year
            if year not in current_purchases:
                current_purchases[year] = {}
                for month_num in range(1, 13):
                    current_purchases[year][str(month_num)] = {}

            cp_year_month_obj = current_purchases[year][month]
            # arr of new purchases on this date
            new_purchases = new_purchase_dates[new_purchase_date]

            for new_purchase in new_purchases:
                if new_purchase_date in cp_year_month_obj:
                    cp_year_month_obj[new_purchase_date].append(new_purchase)
                else:
                    cp_year_month_obj[new_purchase_date] = [new_purchase]

        json.dump(current_purchases_json, db, indent=4)
    
    return 'Successfully updated purchases database with new purchases.', 200

@app.route('/money_spent', methods=['DELETE'])
def delete_purchases():
    delete_purchases_json = request.get_json()
    delete_purchase_dates = delete_purchases_json['purchases']

    current_purchases_json = {}
    with open(DB_FILE_PATH, 'r') as db:
        current_purchases_json = json.load(db)
    current_purchases = current_purchases_json['purchases']
    
    for date in delete_purchase_dates:
        indices_to_delete = delete_purchase_dates[date]
        delete_purchases_from_date(current_purchases, date, indices_to_delete)

    with open(DB_FILE_PATH, 'w') as db:
        json.dump(current_purchases_json, db, indent=4)

    return 'Successfully deleted purchase records from database.', 200

@app.route('/money_spent/clear_all', methods=['DELETE'])
def clear_all_purchases():
    new_purchases = { 'purchases': {} }

    with open(DB_FILE_PATH, 'w') as db:
        json.dump(new_purchases, db, indent=4)
    
    return 'Successfully deleted all purchase records from database.', 200


if __name__ == '__main__':
    # create tables if they don't exist
    db.create_all()
    app.run(debug=True)