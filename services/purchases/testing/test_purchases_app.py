from testing_purchases_json_objects import testing_objects
import json
import subprocess
import requests
import pytest
import os

APP_PY_PATH = os.path.abspath('app.py')

# TODO - finish this testing file
@pytest.fixture(scope='module', autouse=True)
def start_flask_app():
    # TODO - start Flask app in code
    yield

def test_endpoint_clear_all_purchases():
    # reset database to empty default
    response = requests.delete('http://localhost:5001/purchases/clear_all')
    assert response.status_code == 200

    # verify database is now empty
    response = requests.get('http://localhost:5001/purchases/all')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['clear_all_purchases']

def test_endpoint_post_purchases():
    # reset database to empty default
    response = requests.delete('http://localhost:5001/purchases/clear_all')
    assert response.status_code == 200

    # send first post request
    response = requests.post('http://localhost:5001/purchases', json=testing_objects['post_purchases']['first_post'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5001/purchases/all')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['post_purchases']['first_expected']

    # send second post request
    response = requests.post('http://localhost:5001/purchases', json=testing_objects['post_purchases']['second_post'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5001/purchases/all')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['post_purchases']['second_expected']

def test_endpoint_get_range_of_purchases():
    # reset database to empty default
    response = requests.delete('http://localhost:5001/purchases/clear_all')
    assert response.status_code == 200

    # send get request with no start or end date args
    response = requests.get('http://localhost:5001/purchases/range')
    assert response.status_code == 400

    # send get request with start date after end date
    response = requests.get('http://localhost:5001/purchases/range?start=1/1/2020&end=1/1/2019')
    assert response.status_code == 400

    # test endpoint on empty db
    response = requests.get('http://localhost:5001/purchases/range?start=1/1/2020')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['clear_all_purchases']

    # post some data to db
    response = requests.post('http://localhost:5001/purchases', json=testing_objects['post_purchases']['first_post'])
    assert response.status_code == 200

    # test on real data with only start argument
    response = requests.get('http://localhost:5001/purchases/range?start=11/18/2020')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['get_range_of_purchases']['first_get']

    # test with only end argument
    response = requests.get('http://localhost:5001/purchases/range?end=8/21/2021')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['get_range_of_purchases']['second_get']

    # test with start/end arg as same date
    response = requests.get('http://localhost:5001/purchases/range?start=11/19/2020&end=11/19/2020')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['get_range_of_purchases']['third_get']

def test_endpoint_get_category_summation():
        # reset database to empty default
        response = requests.delete('http://localhost:5001/purchases/clear_all')
        assert response.status_code == 200

        # send get request with no start or end date args
        response = requests.get('http://localhost:5001/purchases/category_summation')
        assert response.status_code == 400

        # send get request with start date after end date
        response = requests.get('http://localhost:5001/purchases/category_summation?start=1/1/2020&end=1/1/2019')
        assert response.status_code == 400

        # test endpoint on empty db
        response = requests.get('http://localhost:5001/purchases/category_summation?start=10/9/2020')
        assert response.status_code == 200
        data = response.json()
        assert data == testing_objects['get_category_summation']['first_get']

        # post some data to db
        response = requests.post('http://localhost:5001/purchases', json=testing_objects['post_purchases']['first_post'])
        assert response.status_code == 200
        response = requests.post('http://localhost:5001/purchases', json=testing_objects['post_purchases']['second_post'])
        assert response.status_code == 200

        # test on data with only end argument
        response = requests.get('http://localhost:5001/purchases/category_summation?end=3/3/2021')
        assert response.status_code == 200
        data = response.json()
        assert data == testing_objects['get_category_summation']['second_get']

        # test with start and end argument
        response = requests.get('http://localhost:5001/purchases/category_summation?start=11/18/2020&end=10/21/2023')
        assert response.status_code == 200
        data = response.json()
        assert data == testing_objects['get_category_summation']['third_get']

def test_endpoint_delete_purchases():
    # reset database to empty default
    response = requests.delete('http://localhost:5001/purchases/clear_all')
    assert response.status_code == 200

    # test endpoint on empty db
    response = requests.delete('http://localhost:5001/purchases', json=testing_objects['delete_purchases']['first_delete'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5001/purchases/all')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['clear_all_purchases']

    # post some data to db
    response = requests.post('http://localhost:5001/purchases', json=testing_objects['post_purchases']['first_post'])
    assert response.status_code == 200

    # test delete with data in db
    response = requests.delete('http://localhost:5001/purchases', json=testing_objects['delete_purchases']['first_delete'])
    assert response.status_code == 200
    response = requests.get('http://localhost:5001/purchases/all')
    assert response.status_code == 200
    data = response.json()
    assert data == testing_objects['delete_purchases']['first_expected']
