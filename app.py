from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/TODO', methods=['POST'])
def add_transactions():
    return "TODO"

@app.route('/TODO1', methods=['GET'])
def generate_report():
    return jsonify({
        "TODO": "TODO",
    })

if __name__ == '__main__':
    app.run(debug=True)