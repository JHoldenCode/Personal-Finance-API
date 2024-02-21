from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
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

def set_start_end_date_defaults(start_date, end_date):
    if not start_date:
        # set arbitrary start date from long ago to include purchases up until end_date
        start_date = '9/15/1215'
    if not end_date:
        # set arbitrary end date far in future to include purchases after start date
        end_date = '1/24/5090'

    return start_date, end_date

def verify_chronological_order(start_date, end_date):
    # check that end date is after or on same day as start date
    start_date_timestamp = datetime.strptime(start_date, '%m/%d/%Y')
    end_date_timestamp = datetime.strptime(end_date, '%m/%d/%Y')
    if start_date_timestamp > end_date_timestamp:
        raise ValueError
    
    return start_date_timestamp, end_date_timestamp

def sum_purchases_on_date(summation_dict, purchases_on_date):
    for purchase_obj in purchases_on_date:
        category = purchase_obj['category']
        amount = purchase_obj['amount']
        summation_dict[category] += amount

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

    for purchase in all_purchases:
        purchase_data = {
            'id': purchase.id,
            'date': purchase.date,
            'amount': purchase.amount,
            'memo': purchase.memo,
            'category': purchase.category
        }

        return_json['purchases'].append(purchase_data)

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

# arguments: start, end -> str in M-D-Y format
@app.route('/money_spent/range_of_purchases', methods=['GET'])
def get_range_of_purchases():
    NO_ARG_MSG = "Must submit a start and/or end date for this endpoint using the args 'start' and 'end'.\nUse the /money_spent/all_purchases endpoint to get all purchase records."
    NO_ARG_ERR_CODE = 401
    NOT_CHRONO_MSG = 'Unable to retrieve purchases in a range where start date is after end date.'
    NOT_CHRONO_ERR_CODE = 402

    # get arguments for start and end dates inclusive
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    if not start_date and not end_date:
        return NO_ARG_MSG, NO_ARG_ERR_CODE
    start_date, end_date = set_start_end_date_defaults(start_date, end_date)

    try:
        start_date_timestamp, end_date_timestamp = verify_chronological_order(start_date, end_date)
    except ValueError:
        return NOT_CHRONO_MSG, NOT_CHRONO_ERR_CODE

    # TODO - ensure dates are in correct MM-DD-YYYY format
    start_month, start_day, start_year = start_date.split('/')
    end_month, end_day, end_year = end_date.split('/')

    # append purchase data within range of dates to return_json
    return_json = {'purchases': {}}
    with open(DB_FILE_PATH, 'r') as db:
        # get view of current purchases
        current_purchases_json = json.load(db)
        current_purchases = current_purchases_json['purchases']

        for year in current_purchases:
            if year >= start_year and year <= end_year:
                for month in current_purchases[year]:
                    for date in current_purchases[year][month]:
                        date_timestamp = datetime.strptime(date, '%m/%d/%Y')
                        if date_timestamp >= start_date_timestamp and date_timestamp <= end_date_timestamp:
                            transfer_purchases_from_json(return_json['purchases'], current_purchases, date)

    return jsonify(return_json), 200

# arguments: start, end -> str in M-D-Y format
@app.route('/money_spent/category_summation', methods=['GET'])
def get_category_summation():
    NOT_CHRONO_MSG = 'Unable to retrieve purchases in a range where start date is after end date.'
    NOT_CHRONO_ERR_CODE = 402

    # get arguments for start and end dates inclusive
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    start_date, end_date = set_start_end_date_defaults(start_date, end_date)

    try:
        start_date_timestamp, end_date_timestamp = verify_chronological_order(start_date, end_date)
    except ValueError:
        return NOT_CHRONO_MSG, NOT_CHRONO_ERR_CODE

    start_month, start_day, start_year = start_date.split('/')
    end_month, end_day, end_year = end_date.split('/')

    category_summation_dict = {}
    category_summation_dict['categories'] = defaultdict(float)
    current_purchases = {}
    with open(DB_FILE_PATH, 'r') as db:
        # get view of current purchases
        current_purchases_json = json.load(db)
        current_purchases = current_purchases_json['purchases']

    # TODO - modularize this code with similar code in get_range_of_purchases()
    for year in current_purchases:
        if year >= start_year and year <= end_year:
            for month in current_purchases[year]:
                for date in current_purchases[year][month]:
                    date_timestamp = datetime.strptime(date, '%m/%d/%Y')
                    if date_timestamp >= start_date_timestamp and date_timestamp <= end_date_timestamp:
                        purchases_on_date = current_purchases[year][month][date]
                        sum_purchases_on_date(category_summation_dict['categories'], purchases_on_date)

    category_summation_dict['date_range'] = {
        'start_date': start_date,
        'end_date': end_date
    }

    return jsonify(category_summation_dict), 200

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