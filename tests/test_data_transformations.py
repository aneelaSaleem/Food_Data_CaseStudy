import numpy as np
import pandas as pd

from food_data_processor.transformations.data_transformations import (
    create_categories_count_df, create_categories_min_max_df,
    find_min_max_generic_name, flatten_categories, replace_missing_values,
    transform_categories)


def test_transform_categories():
    df = pd.DataFrame({'categories_hierarchy': ['en:breakfasts en:spreads en:sweet-spreads fr:pates-a-tartiner']})
    result = transform_categories(df)
    expected = np.array(['breakfasts', 'spreads', 'sweet-spreads', 'pates-a-tartiner'])
    np.testing.assert_array_equal(result['categories_hierarchy'].iloc[0], expected)


def test_flatten_categories():
    df = pd.DataFrame({'categories_hierarchy': [['breakfasts', 'spreads', 'sweet-spreads', 'pates-a-tartiner']]})
    result = flatten_categories(df)
    expected = pd.DataFrame({'categories_hierarchy': ['breakfasts', 'spreads', 'sweet-spreads', 'pates-a-tartiner']})
    pd.testing.assert_frame_equal(result, expected)


def test_create_categories_count_df():
    df = pd.DataFrame({'categories_hierarchy': ['breakfasts', 'sweet-spreads', 'breakfasts'], 'id': [1, 2, 3]})
    result = create_categories_count_df(df)
    expected = pd.DataFrame({'category': ['breakfasts', 'sweet-spreads'], 'count': [2, 1]})
    pd.testing.assert_frame_equal(result, expected)


def test_create_categories_min_max_df():
    categories_count_df = pd.DataFrame({'category': ['breakfasts', 'sweet-spreads', 'spreads'], 'count': [2, 1, 1]})
    df = pd.DataFrame(
        {'categories_hierarchy': ['breakfasts', 'sweet-spreads', 'spreads'], 'nutriscore_score': [5, 6, 7]})
    result = create_categories_min_max_df(df, categories_count_df)
    expected = pd.DataFrame({'category': ['breakfasts', 'sweet-spreads', 'spreads'], 'count': [2, 1, 1],
                             'category_name_min': ['breakfasts', None, None],
                             'category_name_max': [None, None, 'spreads']})
    pd.testing.assert_frame_equal(result, expected)


def test_find_min_max_generic_name():
    df = pd.DataFrame({'nutriscore_score': [5, 6, 7], 'generic_name': ['Rice Noodles', 'Sauce Ketchup', 'basil pesto']})
    result = find_min_max_generic_name(df)
    expected = pd.DataFrame({'min_generic_name': ['Rice Noodles'], 'max_generic_name': ['basil pesto']})
    pd.testing.assert_frame_equal(result, expected)


def test_replace_missing_values():
    df = pd.DataFrame({'origins': [None, 'usa', 'france', 'usa']})
    df = replace_missing_values(df)

    assert df['origins'].isnull().sum() == 0

    mode = df['origins'].mode().iloc[0]
    assert (df['origins'] == mode).sum() == 3
