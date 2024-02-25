from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
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

def convert_relation_to_json(relation):
    json_obj = { 'purchases': [] }
    for purchase in relation:
        formatted_date = purchase.date.strftime('%m/%d/%Y')

        purchase_data = {
            'id': purchase.id,
            'date': formatted_date,
            'amount': purchase.amount,
            'memo': purchase.memo,
            'category': purchase.category
        }

        json_obj['purchases'].append(purchase_data)

    return json_obj

def validate_date_arguments(start_date, end_date):
    NO_ARG_MSG = "Must submit a start and/or end date for this endpoint using the args 'start' and 'end'.\nUse the /purchases/all endpoint to get all purchase records."

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
    

# ROUTES

# returns whole DB file
@app.route('/purchases/all', methods=['GET'])
def get_all_purchases():
    # return results sorted so it will be easier to implement the client side purchases table
    all_purchases = Purchases.query.order_by(Purchases.date, Purchases.id).all()
    return_json = convert_relation_to_json(all_purchases)

    return jsonify(return_json), 200

# arguments: start, end -> str in MM/DD/YYYY format
@app.route('/purchases/range', methods=['GET'])
def get_range_of_purchases():
    # get arguments for start and end dates inclusive
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    # validate arguments
    try:
        start_date, end_date = validate_date_arguments(start_date, end_date)
        start_date_timestamp, end_date_timestamp = verify_chronological_order(start_date, end_date)
    except ValueError as err:
        return str(err), 400

    purchases_in_date_range = Purchases.query.filter(Purchases.date.between(start_date_timestamp, end_date_timestamp)) \
        .order_by(Purchases.date, Purchases.id).all()
    return_json = convert_relation_to_json(purchases_in_date_range)

    return jsonify(return_json), 200

# arguments: start, end -> str in MM/DD/YYYY format
@app.route('/purchases/category_summation', methods=['GET'])
def get_category_summation():
    # get arguments for start and end dates inclusive
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    # validate arguments
    try:
        start_date, end_date = validate_date_arguments(start_date, end_date)
        start_date_timestamp, end_date_timestamp = verify_chronological_order(start_date, end_date)
    except ValueError as err:
        return str(err), 400

    return_json = { 'categories': {} }

    # gets the sum of all purchases in each category returned as a list of tuples
    category_summation = category_summation_query(start_date_timestamp, end_date_timestamp)
    for category, amount in category_summation:
        if not category:
            category = 'No Category'
        return_json['categories'][category] = amount

    return_json['date_range'] = {
        'start_date': start_date,
        'end_date': end_date
    }

    return jsonify(return_json), 200

@app.route('/purchases', methods=['POST'])
def post_purchases():
    # TODO - input data verification to ensure that there is an amount and date listed
    try:
        # date field in inputs are of the format YYYY-MM-DD
        input_purchases = request.get_json()['purchases']

        for purchase in input_purchases:
            # TODO - check if its needed to make this obj or if could just use purchase
            new_purchase = Purchases(
                date = purchase['date'],
                amount = purchase['amount'],
                memo = purchase.get('memo') or None,
                category = purchase.get('category') or None
            )

            db.session.add(new_purchase)

        db.session.commit()

        return 'Successfully update purchases database with new purchases.', 200
    except Exception as e:
        return f'Error: {str(e)}', 500

@app.route('/purchases', methods=['DELETE'])
def delete_purchases():
    delete_purchases_with_ids = request.get_json()['purchases']

    try:
        for purchase_id in delete_purchases_with_ids:
            Purchases.query.filter_by(id=purchase_id).delete()

        db.session.commit()

        return 'Successfully deleted purchase records from database.', 200
    except SQLAlchemyError as e:
        db.session.rollback()
        error_msg = f"Error deleting purchase records: {str(e)}"
        return error_msg, 500

@app.route('/purchases/clear_all', methods=['DELETE'])
def clear_all_purchases():
    try:
        # Use db.session.query.delete() to delete all records in the Purchases table
        db.session.query(Purchases).delete()
        db.session.execute(text('ALTER TABLE Purchases AUTO_INCREMENT = 1'))
        db.session.commit()

        return 'Successfully deleted all purchase records from database.', 200
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error clearing all purchase records: {str(e)}"
        return error_msg, 500


if __name__ == '__main__':
    # create tables if they don't exist
    db.create_all()
    app.run(debug=True)