from flask import Flask, request, jsonify
import json

app = Flask(__name__)
DB_FILE_PATH = 'database/current_holdings.json'

@app.route('/holdings', methods=['POST'])
def post_holdings():
    # access holdings submitted to endpoint
    new_holdings = request.get_json()['holdings']

    # update and add from new holdings
    with open(DB_FILE_PATH, 'r+') as db:
        # get view of current_holdings
        current_holdings_json = json.load(db)
        current_holdings = current_holdings_json['holdings']
        
        # move cursor to top so file write begins at correct spot
        # do not need to delete all contents because new file will be at
        # least as long as old file
        db.seek(0)
        for new_holding in new_holdings:
            # update current holding with new data
            if new_holding in current_holdings:
                ch = current_holdings[new_holding]
                nh = new_holdings[new_holding]
                ch['price'] = nh['price']
                ch['shares'] = nh['shares']
                ch['cost_basis'] = nh['cost_basis']
            else: # add new holding data
                current_holdings[new_holding] = new_holdings[new_holding]

        # Write the updated data back to the file
        json.dump(current_holdings_json, db, indent=4)

    return "Successfully updated holdings database.", 200

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

@app.route('/clear_all_holdings', methods=['DELETE'])
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
        holding_info['percent_gain'] = round((price - cost_basis) / cost_basis * 100, 3)

        # increment sums of equity and dollars gained
        total_equity += equity
        total_dollar_gain += dollar_gain
    
    # append separate JSON object of sums
    total_percent_gain = round(total_equity / (total_equity - total_dollar_gain) - 1, 3)
    current_holdings_json['compiled_stats'] = {
        'total_equity': total_equity,
        'total_dollar_gain': total_dollar_gain,
        'total_percent_gain': total_percent_gain
    }

    return current_holdings_json, 200


if __name__ == '__main__':
    app.run(debug=True)