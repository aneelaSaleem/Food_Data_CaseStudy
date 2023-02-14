import numpy as np
import pandas as pd


def transform_categories(df):
    df["categories_hierarchy"] = df["categories_hierarchy"].apply(
        lambda x: np.array(list(map(lambda category: category.split(":")[-1].strip().lower(), x.split(" ")))))
    return df


def flatten_categories(df):
    df = df.explode("categories_hierarchy").reset_index(drop=True)
    df["categories_hierarchy"] = df["categories_hierarchy"].astype(str)
    return df


###########################
# Task 2.a
###########################

def create_categories_count_df(df):
    categories_df = df.groupby(["categories_hierarchy"])["id"].count().reset_index(
        name="count").rename(columns={"categories_hierarchy": "category"})
    return categories_df


###########################
# Task 2.b
###########################


def create_categories_min_max_df(df, categories_count_df):

    min_categories_df = df[df.nutriscore_score == df.nutriscore_score.min()]["categories_hierarchy"].to_frame()
    max_categories_df = df[df.nutriscore_score == df.nutriscore_score.max()]["categories_hierarchy"].to_frame()

    min_categories_df.rename(columns={"categories_hierarchy": "category_name_min"}, inplace=True)
    max_categories_df.rename(columns={"categories_hierarchy": "category_name_max"}, inplace=True)

    categories_count_df = pd.merge(categories_count_df, min_categories_df,
                                   left_on=["category"], right_on=["category_name_min"], how="left")
    categories_count_df = pd.merge(categories_count_df, max_categories_df,
                                   left_on=["category"], right_on=["category_name_max"], how="left")

    return categories_count_df


###########################
# Task 2.c
###########################

def find_min_max_generic_name(df):
    min_index = df["nutriscore_score"].idxmin()
    min_generic_name = df.loc[min_index, "generic_name"]
    max_index = df["nutriscore_score"].idxmax()
    max_generic_name = df.loc[max_index, "generic_name"]

    min_max_gn_df = pd.DataFrame({"min_generic_name": [min_generic_name],
                                  "max_generic_name": [max_generic_name]})
    return min_max_gn_df


###########################
# Task 2.d
###########################

def replace_missing_values(df):
    df["origins"].fillna(df["origins"].mode().iloc[0], inplace=True)
    return df
