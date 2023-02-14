import abc
import logging

import pandas as pd
import sqlalchemy
from sqlalchemy import Engine


class AbstractDataSink(metaclass=abc.ABCMeta):
    name = ""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abc.abstractmethod
    def save_data(self) -> bool:
        pass


class CSVDataSink(AbstractDataSink):
    def __init__(self, df: pd.DataFrame, write_path: str):
        super().__init__(df)
        self.name = "CSV"
        self.write_path = write_path

    def save_data(self, ) -> bool:
        try:
            self.df["categories_hierarchy"] = self.df["categories_hierarchy"].apply(lambda x: " ".join(x))
            self.df.to_csv(self.write_path, index=False)
            return True
        except Exception as e:
            logging.exception(e)
            return False


class DBDataSink(AbstractDataSink):

    def __init__(self, df: pd.DataFrame, connection_props: dict):
        super().__init__(df)
        self.name = "PostgresDb"
        self.connection_props = connection_props

    def __get_db_engine(self) -> Engine:
        user = self.connection_props["username"]
        password = self.connection_props["password"]
        host = self.connection_props["host"]
        db_name = self.connection_props["db_name"]
        connection_str = f"postgresql://{user}:{password}@{host}/{db_name}"
        engine = sqlalchemy.create_engine(connection_str)
        return engine

    def save_data(self) -> bool:
        try:
            self.df.rename(columns={"id": "product_id", "generic_name": "product_name"}, inplace=True)
            engine = self.__get_db_engine()
            table_name = self.connection_props["table"]
            self.df.to_sql(
                name=table_name,
                con=engine,
                if_exists="replace",
                index=False,
                method="multi"
            )

            with engine.connect() as con:
                con.execute(sqlalchemy.text(f"ALTER TABLE {table_name} ADD PRIMARY KEY (product_id)"))
            return True
        except Exception as e:
            logging.exception(e)
            return False
