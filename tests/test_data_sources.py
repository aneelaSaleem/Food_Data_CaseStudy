import os

import pandas as pd
import pytest
import requests_mock

from food_data_processor.sources.data_source import (APIDataSource,
                                                     CSVDataSource)


def test_CSVDataSource_fetch_data():
    file_path = 'test.csv'
    with open(file_path, 'w') as f:
        f.write('id,product,origins\n1,basil pesto,Thailand\n2,Snack salé,France\n')
    csv_datasource = CSVDataSource(file_path)
    result = csv_datasource.fetch_data()
    expected = pd.DataFrame({'id': [1, 2], 'product': ['basil pesto', 'Snack salé'], 'origins': ['Thailand', 'France']})
    pd.testing.assert_frame_equal(result, expected)
    os.remove(file_path)


def test_CSVDataSource_fetch_data_exception():
    file_path = 'invalid.csv'
    csv_datasource = CSVDataSource(file_path)
    with pytest.raises(Exception) as e:
        csv_datasource.fetch_data()
    assert str(e.value) == f'Invalid file path. File {file_path} does not exist'


def test_APIDataSource_fetch_data():
    endpoint = 'https://api.openfoodfacts.org/v0/product'
    product_ids = ['12345', '67890']
    with requests_mock.Mocker() as m:
        for product_id in product_ids:
            url = f'{endpoint}/{product_id}.json'
            product_data = {
                "product": {
                    "categories_hierarchy": [
                        "en:beverages",
                        "en:sweet-beverages"
                    ],
                    "generic_name": "Boisson rafraîchissante aux extraits végétaux, avec édulcorants",
                    "nutriscore_score": 0,
                    "quantity": "1L",
                    "origins": "France",
                    "allergens": "None",
                    "debug_param_sorted_langs": [
                        "en",
                        "fr",
                        "es"
                    ]
                }
            }
            m.get(url, json=product_data)
        api_datasource = APIDataSource(endpoint, product_ids)
        result = api_datasource.fetch_data()
        expected = pd.DataFrame({
            'id': product_ids,
            'categories_hierarchy': [['en:beverages', 'en:sweet-beverages'], ['en:beverages', 'en:sweet-beverages']],
            'generic_name': ['Boisson rafraîchissante aux extraits végétaux, avec édulcorants',
                             'Boisson rafraîchissante aux extraits végétaux, avec édulcorants'],
            'nutriscore_score': [0, 0],
            'quantity': ['1L', '1L'],
            'origins': ['France', 'France'],
            'allergens': ['None', 'None']
        })
        pd.testing.assert_frame_equal(result, expected)
