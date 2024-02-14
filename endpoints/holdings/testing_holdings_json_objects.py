testing_objects = {
    'clear_all_holdings': {
        'compiled_stats': {
            'total_dollar_gain': 0,
            'total_equity': 0,
            'total_percent_gain': 0
        },
        'holdings': {}
    },
    'post_holdings': {
        'first_post': {
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
        },
        'first_expected': {
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
        },
        'second_post': {
            'holdings': {
                'NVDA': {
                    'price': 89.75,
                    'shares': 2.3,
                    'cost_basis': 90.00
                },
                'MSFT': {
                    'price': 58.95,
                    'shares': 12.33,
                    'cost_basis': 49.42
                },
                'SNAP': {
                    'price': 15,
                    'shares': 8.7,
                    'cost_basis': 22.60
                }
            }
        },
        'second_expected': {
            'compiled_stats' : {
                'total_dollar_gain': 61.26,
                'total_equity': 1204.579,
                'total_percent_gain': 0.054
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
                'NVDA': {
                    'cost_basis': 90.0,
                    'dollar_gain': -0.575,
                    'equity': 206.425,
                    'percent_gain': -0.278,
                    'price': 89.75,
                    'shares': 2.3,
                },
                'SNAP': {
                    'price': 15,
                    'dollar_gain': -66.12,
                    'equity': 130.5,
                    'percent_gain': -33.628,
                    'shares': 8.7,
                    'cost_basis': 22.60
                }
            }
        }
    },
    'delete_holdings': {
        'first_delete': {
            'holdings': [
                'AAPL',
                'MSFT'
            ]
        },
        'second_delete': {
            'holdings': [
                'MSFT',
                'ETSY'
            ]
        },
        'third_delete': {
            'holdings': []
        },
        'delete_expected': {
            'compiled_stats' : {
                'total_dollar_gain': -21.47,
                'total_equity': 203.8,
                'total_percent_gain': -0.095
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
    }
}