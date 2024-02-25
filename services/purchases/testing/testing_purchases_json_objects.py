testing_objects = {
    'clear_all_purchases': {
        'purchases': []
    },
    'post_purchases': {
        'first_post': {
            'purchases': [
                { "date": "11/17/2020", "amount": 95, "memo": "car_insurance", "category": "necessity"},
                { "date": "11/19/2020", "amount": 1.56},
                { "date": "11/17/2020", "amount": 33.56, "memo": "sweatshirt", "category": "discretionary"},
                { "date": "11/17/2020", "amount": 325.99, "memo": "steak dinner", "category": "food"},
                { "date": "11/19/2020", "amount": 68.00, "category": "entertainment"},
                { "date": "1/3/2023", "amount": 20, "memo": "haircut"},
                { "date": "1/03/2020", "amount": 26, "memo": "bww", "category": "food"}
            ]
        },
        'first_expected': {
            "purchases": [
                { "id": 7, "date": "01/03/2020", "amount": 26.0, "memo": "bww", "category": "food"},
                { "id": 1, "date": "11/17/2020", "amount": 95.0, "memo": "car_insurance", "category": "necessity"},
                { "id": 3, "date": "11/17/2020", "amount": 33.56, "memo": "sweatshirt", "category": "discretionary"},
                { "id": 4, "date": "11/17/2020", "amount": 325.99, "memo": "steak dinner", "category": "food"},
                { "id": 2, "date": "11/19/2020", "amount": 1.56, "memo": None, "category": None},
                { "id": 5, "date": "11/19/2020", "amount": 68.00, "memo": None, "category": "entertainment"},
                { "id": 6, "date": "01/03/2023", "amount": 20.0, "memo": "haircut", "category": None}
            ]
        },
        'second_post': {
            'purchases': [
                { "date": "11/17/2020", "amount": 95, "memo": "car_insurance", "category": "necessity"},
                { "date": "11/17/2020", "amount": 45.44, "memo": "socks", "category": "necessity"},
                { "date": "10/31/2023", "amount": 30, "memo": "costume", "category": "entertainment"},
            ]
        },
        'second_expected': {
            "purchases": [
                { "id": 7, "date": "01/03/2020", "amount": 26.0, "memo": "bww", "category": "food"},
                { "id": 1, "date": "11/17/2020", "amount": 95.0, "memo": "car_insurance", "category": "necessity"},
                { "id": 3, "date": "11/17/2020", "amount": 33.56, "memo": "sweatshirt", "category": "discretionary"},
                { "id": 4, "date": "11/17/2020", "amount": 325.99, "memo": "steak dinner", "category": "food"},
                { "id": 8, "date": "11/17/2020", "amount": 95, "memo": "car_insurance", "category": "necessity"},
                { "id": 9, "date": "11/17/2020", "amount": 45.44, "memo": "socks", "category": "necessity"},
                { "id": 2, "date": "11/19/2020", "amount": 1.56, "memo": None, "category": None},
                { "id": 5, "date": "11/19/2020", "amount": 68.00, "memo": None, "category": "entertainment"},
                { "id": 6, "date": "01/03/2023", "amount": 20.0, "memo": "haircut", "category": None},
                { "id": 10, "date": "10/31/2023", "amount": 30, "memo": "costume", "category": "entertainment"}
            ]
        }
    },
    'get_range_of_purchases': {
        'first_get': {
            'purchases': [
                { "id": 2, "date": "11/19/2020", "amount": 1.56, "memo": None, "category": None},
                { "id": 5, "date": "11/19/2020", "amount": 68.00, "memo": None, "category": "entertainment"},
                { "id": 6, "date": "01/03/2023", "amount": 20.0, "memo": "haircut", "category": None}
            ]
        },
        'second_get': {
            "purchases": [
                { "id": 7, "date": "01/03/2020", "amount": 26.0, "memo": "bww", "category": "food"},
                { "id": 1, "date": "11/17/2020", "amount": 95.0, "memo": "car_insurance", "category": "necessity"},
                { "id": 3, "date": "11/17/2020", "amount": 33.56, "memo": "sweatshirt", "category": "discretionary"},
                { "id": 4, "date": "11/17/2020", "amount": 325.99, "memo": "steak dinner", "category": "food"},
                { "id": 2, "date": "11/19/2020", "amount": 1.56, "memo": None, "category": None},
                { "id": 5, "date": "11/19/2020", "amount": 68.00, "memo": None, "category": "entertainment"}
            ]
        },
        'third_get': {
            'purchases': [
                { "id": 2, "date": "11/19/2020", "amount": 1.56, "memo": None, "category": None},
                { "id": 5, "date": "11/19/2020", "amount": 68.00, "memo": None, "category": "entertainment"},
            ]
        }
    },
    'get_category_summation': {
        'first_get': {
            'categories': {},
            'date_range': {
                'start_date': '10/9/2020',
                'end_date': '1/24/5090'
            }
        },
        'second_get': {
            'categories': {
                'food': 351.99,
                'necessity': 235.44,
                'No Category': 1.56,
                'discretionary': 33.56,
                'entertainment': 68.0
            },
            'date_range': {
                'start_date': '9/15/1215',
                'end_date': '3/3/2021'
            }
        },
        'third_get': {
            'categories': {
                'No Category': 21.56,
                'entertainment': 68.0
            },
            'date_range': {
                'start_date': '11/18/2020',
                'end_date': '10/21/2023'
            }
        }
    },
    'delete_purchases': {
        'first_delete': {
            'purchases': [ 1, 4, 5 ]
        },
        'first_expected': {
            'purchases': [
                { "id": 7, "date": "01/03/2020", "amount": 26.0, "memo": "bww", "category": "food"},
                { "id": 3, "date": "11/17/2020", "amount": 33.56, "memo": "sweatshirt", "category": "discretionary"},
                { "id": 2, "date": "11/19/2020", "amount": 1.56, "memo": None, "category": None},
                { "id": 6, "date": "01/03/2023", "amount": 20.0, "memo": "haircut", "category": None}
            ]
        }
    }
}