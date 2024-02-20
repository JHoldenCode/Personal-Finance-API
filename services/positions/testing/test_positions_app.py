from test_positions_json_objects import testing_objects
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

def test_endpoint_clear_all_positions():
    # TODO - run tests on separate database?
    # reset database to empty default
    response = requests.delete('http://localhost:5000/positions/clear_all')
    assert response.status_code == 200

    # verify database is now empty
    response = requests.get('http://localhost:5000/positions')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['clear_all_positions']

def test_endpoint_post_positions():
    # reset database to empty default
    response = requests.delete('http://localhost:5000/positions/clear_all')
    assert response.status_code == 200

    # post new data to empty db and assert get positions report is correct
    response = requests.post('http://localhost:5000/positions', json=testing_objects['post_positions']['first_post'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5000/positions')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['post_positions']['first_expected']

    # post new stock, update stock, one stock same
    response = requests.post('http://localhost:5000/positions', json=testing_objects['post_positions']['second_post'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5000/positions')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['post_positions']['second_expected']

def test_endpoint_delete_positions():
    # reset database to empty default
    response = requests.delete('http://localhost:5000/positions/clear_all')
    assert response.status_code == 200

    # try deleting from empty database
    response = requests.delete('http://localhost:5000/positions', json=testing_objects['delete_positions']['first_delete'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5000/positions')
    assert response.status_code == 200
    data = response.json()
    # reuse testing object since it should be completely empty
    assert data == testing_objects['clear_all_positions']

    # insert some data and try deleting stocks in database and stocks not
    response = requests.post('http://localhost:5000/positions', json=testing_objects['post_positions']['first_post'])
    assert response.status_code == 200
    response = requests.delete('http://localhost:5000/positions', json=testing_objects['delete_positions']['second_delete'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5000/positions')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['delete_positions']['delete_expected']

    # send a delete request with nothing in delete input array
    response = requests.delete('http://localhost:5000/positions', json=testing_objects['delete_positions']['third_delete'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5000/positions')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['delete_positions']['delete_expected']
