import json
import subprocess
import requests
import pytest
import os

APP_PY_PATH = os.path.abspath('app.py')

@pytest.fixture(scope='module', autouse=True)
def start_flask_app():
    # TODO - moduleNotFoundError for flask when started here
    # Setup: Start the Flask application in a separate process
    # flask_process = subprocess.Popen(['python', APP_PY_PATH])

    yield  # This is where the test execution happens

    # Teardown: Terminate the Flask process after all tests are done
    # flask_process.terminate()

def test_endpoint_clear_all_holdings():
    # TODO - run tests on separate file, figure out how to pass args to endpoints
    # reset database to empty default
    response = requests.delete('http://localhost:5000/clear_all_holdings')
    assert response.status_code == 200

    # ensure that get holdings report represents database with empty data
    expected_json = { 
        'compiled_stats' : {
            'total_dollar_gain': 0,
            'total_equity': 0,
            'total_percent_gain': 0
        },
        'holdings': {}
    }
    response = requests.get('http://localhost:5000/holdings')
    assert response.status_code == 200
    data = response.json()
    assert data == expected_json

def test_endpoint_post_holdings():
    # reset database to empty default
    response = requests.delete('http://localhost:5000/clear_all_holdings')
    assert response.status_code == 200

    # post new data to empty db and assert get holdings report is correct
    new_data_to_post = {
        'holdings': {
            'AAPL': {
                'price': 25.60,
                'shares': 5.5,
                'cost_basis': 23.70
            },
            'MSFT': {
                'price': 58.95,
                'shares': 12.33,
                'cost_basis': 49.42
            },
            'SNAP': {
                'price': 15,
                'shares': 4.2,
                'cost_basis': 22.60
            }
        }
    }
    # TODO - verify that this is accurate
    expected_json = { 
        'compiled_stats' : {
            'total_dollar_gain': 96.035,
            'total_equity': 930.654,
            'total_percent_gain': 0.115
        },
        'holdings': {
            'AAPL': {
                'price': 25.60,
                'dollar_gain': 10.45,
                'equity': 140.8,
                'percent_gain': 8.017,
                'shares': 5.5,
                'cost_basis': 23.70
            },
            'MSFT': {
                'price': 58.95,
                'dollar_gain': 117.505,
                'equity': 726.854,
                'percent_gain': 19.284,
                'shares': 12.33,
                'cost_basis': 49.42
            },
            'SNAP': {
                'price': 15,
                'dollar_gain': -31.92,
                'equity': 63.0,
                'percent_gain': -33.628,
                'shares': 4.2,
                'cost_basis': 22.60
            }
        }
    }

    response = requests.post('http://localhost:5000/holdings', json=new_data_to_post)
    assert response.status_code == 200
    response = requests.get('http://localhost:5000/holdings')
    assert response.status_code == 200
    data = response.json()
    assert data == expected_json

# def test_endpoint_post_holdings():
#     # 

#     response = requests.get('http://localhost:5000/endpoint_one')
#     assert response.status_code == 200
#     data = response.json()
#     # Add assertions to verify the correctness of the returned data

# def test_endpoint_two():
#     # Test the second endpoint
#     payload = {'key': 'value'}
#     response = requests.post('http://localhost:5000/endpoint_two', json=payload)
#     assert response.status_code == 200
#     data = response.json()
#     # Add assertions to verify the correctness of the returned data
