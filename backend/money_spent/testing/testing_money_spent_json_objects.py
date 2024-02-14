testing_objects = {
    'clear_all_purchases': {
        'purchases': {}
    },
    'post_money_spent': {
        'first_post': {
            'purchases': {
                "11/17/2020": [
                    { "amount": 95, "item": "car_insurance", "category": "necessity"},
                    { "amount": 33.56, "item": "sweatshirt", "category": "discretionary"},
                    {"amount": 325.99, "item": "steak dinner", "category": "food"}
                ],
                "11/19/2020": [
                    {"amount": 1.56, "item": "sales tax", "category": "necessity"},
                    {"amount": 68.00, "item": "bill burr show", "category": "entertainment"}
                ],
                "1/3/2023": [
                    {"amount": 20, "item": "haircut", "category": "necessity"},
                    {"amount": 26, "item": "bww", "category": "food"}
                ]
            }
        },
        'first_expected': {
            "purchases": {
                "2020": {
                    "1": {},
                    "2": {},
                    "3": {},
                    "4": {},
                    "5": {},
                    "6": {},
                    "7": {},
                    "8": {},
                    "9": {},
                    "10": {},
                    "11": {
                        "11/17/2020": [
                            {
                                "amount": 95,
                                "item": "car_insurance",
                                "category": "necessity"
                            },
                            {
                                "amount": 33.56,
                                "item": "sweatshirt",
                                "category": "discretionary"
                            },
                            {
                                "amount": 325.99,
                                "item": "steak dinner",
                                "category": "food"
                            }
                        ],
                        "11/19/2020": [
                            {
                                "amount": 1.56,
                                "item": "sales tax",
                                "category": "necessity"
                            },
                            {
                                "amount": 68.0,
                                "item": "bill burr show",
                                "category": "entertainment"
                            }
                        ]
                    },
                    "12": {}
                },
                "2023": {
                    "1": {
                        "1/3/2023": [
                            {
                                "amount": 20,
                                "item": "haircut",
                                "category": "necessity"
                            },
                            {
                                "amount": 26,
                                "item": "bww",
                                "category": "food"
                            }
                        ]
                    },
                    "2": {},
                    "3": {},
                    "4": {},
                    "5": {},
                    "6": {},
                    "7": {},
                    "8": {},
                    "9": {},
                    "10": {},
                    "11": {},
                    "12": {}
                }
            }
        },
        'second_post': {
            'purchases': {
                "11/17/2020": [
                    { "amount": 95, "item": "car_insurance", "category": "necessity"},
                    { "amount": 45.44, "item": "socks", "category": "necessity"},
                ],
                "10/31/2023": [
                    {"amount": 30, "item": "costume", "category": "entertainment"},
                ],
            }
        },
        'second_expected': {
            'purchases': {
                "2020": {
                    "1": {},
                    "2": {},
                    "3": {},
                    "4": {},
                    "5": {},
                    "6": {},
                    "7": {},
                    "8": {},
                    "9": {},
                    "10": {},
                    "11": {
                        "11/17/2020": [
                            {
                                "amount": 95,
                                "item": "car_insurance",
                                "category": "necessity"
                            },
                            {
                                "amount": 33.56,
                                "item": "sweatshirt",
                                "category": "discretionary"
                            },
                            {
                                "amount": 325.99,
                                "item": "steak dinner",
                                "category": "food"
                            },
                            {
                                "amount": 95,
                                "item": "car_insurance",
                                "category": "necessity"
                            },
                            {
                                "amount": 45.44,
                                "item": "socks",
                                "category": "necessity"
                            }
                        ],
                        "11/19/2020": [
                            {
                                "amount": 1.56,
                                "item": "sales tax",
                                "category": "necessity"
                            },
                            {
                                "amount": 68.0,
                                "item": "bill burr show",
                                "category": "entertainment"
                            }
                        ]
                    },
                    "12": {}
                },
                "2023": {
                    "1": {
                        "1/3/2023": [
                            {
                                "amount": 20,
                                "item": "haircut",
                                "category": "necessity"
                            },
                            {
                                "amount": 26,
                                "item": "bww",
                                "category": "food"
                            }
                        ]
                    },
                    "2": {},
                    "3": {},
                    "4": {},
                    "5": {},
                    "6": {},
                    "7": {},
                    "8": {},
                    "9": {},
                    "10": {
                        "10/31/2023": [
                            {
                                "amount": 30,
                                "item": "costume",
                                "category": "entertainment"
                            }
                        ]
                    },
                    "11": {},
                    "12": {}
                }
            }
        }
    },
    'get_range_of_purchases': {
        'first_get': {
            'purchases': {
                "2023": {
                    "1": {
                        "1/3/2023": [
                            {
                                "amount": 20,
                                "item": "haircut",
                                "category": "necessity"
                            },
                            {
                                "amount": 26,
                                "item": "bww",
                                "category": "food"
                            }
                        ]
                    }
                }
            }
        },
        'second_get': {
            "purchases": {
                "2020": {
                    "11": {
                        "11/17/2020": [
                            {
                                "amount": 95,
                                "item": "car_insurance",
                                "category": "necessity"
                            },
                            {
                                "amount": 33.56,
                                "item": "sweatshirt",
                                "category": "discretionary"
                            },
                            {
                                "amount": 325.99,
                                "item": "steak dinner",
                                "category": "food"
                            }
                        ],
                        "11/19/2020": [
                            {
                                "amount": 1.56,
                                "item": "sales tax",
                                "category": "necessity"
                            },
                            {
                                "amount": 68.0,
                                "item": "bill burr show",
                                "category": "entertainment"
                            }
                        ]
                    }
                }
            }
        },
        'third_get': {
            'purchases': {
                "2020": {
                    "11": {
                        "11/19/2020": [
                            {
                                "amount": 1.56,
                                "item": "sales tax",
                                "category": "necessity"
                            },
                            {
                                "amount": 68.0,
                                "item": "bill burr show",
                                "category": "entertainment"
                            }
                        ]
                    }
                }
            }
        }
    }
}