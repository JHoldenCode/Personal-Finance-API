from flask import Flask, request, jsonify
import json
import request

# example curl request
# curl -X POST http://127.0.0.1:5000/money_spent -H "Content-Type: application/json" -d @input_post_purchases.json
app = Flask(__name__)
DB_FILE_PATH = '../../databases/money_spent/purchases.json'

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

# returns whole DB file
@app.route('/money_spent/all_purchases', methods=['GET'])
def get_all_purchases():
    current_purchases_json = {}
    with open(DB_FILE_PATH, 'r') as db:
        # get view of current purchases
        current_purchases_json = json.load(db)
    
    return current_purchases_json, 200

@app.route('/money_spent/range_of_purchases', methods=['GET'])
def get_range_of_purchases():
    # get arguments for start and end dates inclusive
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    # error handling with date range args
    if not start_date and not end_date:
        return "Must submit a start and/or end date for this endpoint through the args 'start' and 'end'.", 409
    if not start_date:
        # set arbitrary start date from long ago to include purchases up until end_date
        start_date = '9/15/1215'
    elif not end_date:
        # set arbitrary end date far in future to include purchases after start date
        end_date = '1/24/5090'

    



if __name__ == '__main__':
    app.run(debug=True)