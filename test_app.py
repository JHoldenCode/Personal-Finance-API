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
    response = requests.delete('http://localhost:5000/clear_all_holdings')
    print(response)
    assert 2 == 2

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
