import copy
import logging
import os

from dotenv import load_dotenv
from psycopg2.extensions import AsIs, register_adapter
from tabulate import tabulate

from food_data_processor.sinks.data_sinks import CSVDataSink, DBDataSink
from food_data_processor.sources.data_source import (APIDataSource,
                                                     CSVDataSource)
from food_data_processor.transformations.data_transformations import *

load_dotenv()
logging.getLogger().setLevel(logging.INFO)


def adapt_numpy_array(numpy_array):
    return AsIs(tuple(numpy_array))


register_adapter(np.ndarray, adapt_numpy_array)


def env_vars_to_dict():
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_DB"]
    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]

    return {
        "username": user,
        "password": password,
        "db_name": db,
        "host": host,
        "port": port
    }


if __name__ == "__main__":
    BASE_URL = "https://world.openfoodfacts.org/api/v0/product"
    OUTPUT_CSV_PATH = "./data.csv"
    TABLE_NAME = "food_data"

    product_ids = [
        "737628064502", "3017620422003", "5449000131805", "3175680011534",
        "8000500310427", "3228857000166", "3229820782560", "5410188031072",
        "5010477348630", "3068320114453", "3088543506255", "3033490506629",
        "7622210476104", "5000112611878", "3228021170022", "5411188119098",
        "3073781115345", "3252210390014", "20724696", "8076809513753",
        "87157239", "7622300441937", "5053990156009", "20916435"
    ]

    api_source = APIDataSource(BASE_URL, product_ids)
    df = api_source.fetch_data()
    pd.set_option("display.max_columns", None)

    csv_sink = CSVDataSink(df, OUTPUT_CSV_PATH)
    csv_source = CSVDataSource(OUTPUT_CSV_PATH)
    csv_sink.save_data()
    csv_df = csv_source.fetch_data()

    # transformations
    df = transform_categories(csv_df)
    exploded_df = flatten_categories(copy.deepcopy(df))
    category_count_df = create_categories_count_df(exploded_df)
    print(tabulate(category_count_df.head(), headers="keys", tablefmt="psql", showindex=False))
    category_count_min_max_df = create_categories_min_max_df(exploded_df, category_count_df)
    print(tabulate(category_count_min_max_df[
                       (~category_count_min_max_df["category_name_min"].isnull()) |
                       (~category_count_min_max_df["category_name_max"].isnull())]
                   .head(n=10), headers='keys', tablefmt='psql', showindex=False))
    min_max_generic_name = find_min_max_generic_name(df)
    print(tabulate(min_max_generic_name.head(), headers="keys", tablefmt="psql", showindex=False))
    cleaned_df = replace_missing_values(df)
    print(tabulate(cleaned_df[["id", "origins"]].head(n=10), headers="keys", tablefmt="psql", showindex=False))

    props = env_vars_to_dict()
    props["table"] = TABLE_NAME
    db_sink = DBDataSink(df, props)
    db_sink.save_data()
