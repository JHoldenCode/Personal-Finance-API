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


# @app.route('/TODO1', methods=['GET'])
def generate_report():
    return jsonify({
        "TODO": "TODO",
    })

if __name__ == '__main__':
    app.run(debug=True)