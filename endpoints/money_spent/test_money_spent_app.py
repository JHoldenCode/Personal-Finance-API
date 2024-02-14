import json
import subprocess
import requests
import pytest
import os
from testing_money_spent_json_objects import testing_objects

APP_PY_PATH = os.path.abspath('app.py')

# TODO - finish this testing file
@pytest.fixture(scope='module', autouse=True)
def start_flask_app():
    # TODO - start Flask app in code
    yield

def test_endpoint_clear_all_purchases():
    # reset database to empty default
    response = requests.delete('http://localhost:5000/money_spent/clear_all')
    assert response.status_code == 200

    # verify database is now empty
    response = requests.get('http://localhost:5000/money_spent/all_purchases')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['clear_all_purchases']

def test_endpoint_post_money_spent():
    # reset database to empty default
    response = requests.delete('http://localhost:5000/money_spent/clear_all')
    assert response.status_code == 200

    # send first post request
    response = requests.post('http://localhost:5000/money_spent', json=testing_objects['post_money_spent']['first_post'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5000/money_spent/all_purchases')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['post_money_spent']['first_expected']

    # send second post request
    response = requests.post('http://localhost:5000/money_spent', json=testing_objects['post_money_spent']['second_post'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5000/money_spent/all_purchases')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['post_money_spent']['second_expected']

def test_endpoint_get_range_of_purchases():
    # reset database to empty default
    response = requests.delete('http://localhost:5000/money_spent/clear_all')
    assert response.status_code == 200

    # send get request with no start or end date args
    response = requests.get('http://localhost:5000/money_spent/range_of_purchases')
    assert response.status_code == 401

    # send get request with start date after end date
    response = requests.get('http://localhost:5000/money_spent/range_of_purchases?start=1/1/2020&end=1/1/2019')
    assert response.status_code == 402

    # test endpoint on empty db
    response = requests.get('http://localhost:5000/money_spent/range_of_purchases?start=1/1/2020')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['clear_all_purchases']

    # post some data to db
    response = requests.post('http://localhost:5000/money_spent', json=testing_objects['post_money_spent']['first_post'])
    assert response.status_code == 200

    # test on real data with only start argument
    response = requests.get('http://localhost:5000/money_spent/range_of_purchases?start=1/1/2022')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['get_range_of_purchases']['first_get']

    # test with only end argument
    response = requests.get('http://localhost:5000/money_spent/range_of_purchases?end=1/1/2022')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['get_range_of_purchases']['second_get']

    # test with start/end arg as same date
    response = requests.get('http://localhost:5000/money_spent/range_of_purchases?start=11/19/2020&end=11/19/2020')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['get_range_of_purchases']['third_get']

