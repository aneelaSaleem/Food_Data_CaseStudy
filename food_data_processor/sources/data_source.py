import abc
import logging
import os.path
from concurrent.futures import ThreadPoolExecutor
from typing import List

import pandas as pd
import requests


class AbstractDataSource(metaclass=abc.ABCMeta):
    def __init__(self, type: str):
        self.name = type

    @abc.abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        pass


class CSVDataSource(AbstractDataSource):
    def __init__(self, file_path: str):
        super().__init__("CSV")
        self.file_path = file_path

    def fetch_data(self) -> pd.DataFrame:
        if os.path.exists(self.file_path):
            return pd.read_csv(self.file_path)
        else:
            raise Exception(f"Invalid file path. File {self.file_path} does not exist")


class APIDataSource(AbstractDataSource):
    def __init__(self, endpoint: str, product_ids: List[str]):
        super().__init__("API")
        self.endpoint = endpoint
        self.product_ids = product_ids
        self.timeout = 1000

    @staticmethod
    def __get_generic_name(product_info):
        generic_name = product_info.get("generic_name", "")
        if generic_name:
            return product_info["generic_name"]

        all_langs = product_info["debug_param_sorted_langs"]
        for lang in all_langs:
            generic_name_key = f"generic_name_{lang}"
            if generic_name_key in product_info and product_info[generic_name_key]:
                return product_info[generic_name_key]

    def __make_api_call(self, product_id):
        url = f"{self.endpoint}/{product_id}.json"
        response = requests.get(url, timeout=self.timeout)

        if response.status_code == 404:
            return {}
        else:
            data = response.json()
            product_data = {
                "id": product_id,
                "categories_hierarchy": data["product"]["categories_hierarchy"],
                "generic_name": self.__get_generic_name(data["product"]),
                "nutriscore_score": data["product"]["nutriscore_score"],
                "quantity": data["product"]["quantity"],
                "origins": data["product"]["origins"],
                "allergens": data["product"]["allergens"],
            }
            return product_data

    def fetch_data(self) -> pd.DataFrame:
        data = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = [executor.submit(self.__make_api_call, product_id) for product_id in self.product_ids]
            for future in results:
                try:
                    data.append(future.result())
                except requests.ConnectTimeout:
                    logging.error("ConnectTimeout.")
        return pd.DataFrame(data)
