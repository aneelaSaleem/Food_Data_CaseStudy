import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from food_data_processor.sinks.data_sinks import CSVDataSink, DBDataSink


@pytest.fixture
def df():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "generic_name": ["apple", "banana", "cherry"],
        "categories_hierarchy": [["fruit"], ["fruit"], ["fruit"]]
    })


def test_csv_data_sink(df):
    write_path = "test_csv_data_sink.csv"
    data_sink = CSVDataSink(df, write_path)
    assert data_sink.save_data()
    assert os.path.exists(write_path)
    os.remove(write_path)


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_db_data_sink_save_data(df):
    mock_engine = MagicMock()
    connection_props = {
        'username': 'test_user',
        'password': 'test_password',
        'host': 'test_host',
        'db_name': 'test_db',
        'table': 'test_table'
    }
    db_data_sink = DBDataSink(df, connection_props)

    with patch('sqlalchemy.create_engine', return_value=mock_engine):
        result = db_data_sink.save_data()

    assert result
