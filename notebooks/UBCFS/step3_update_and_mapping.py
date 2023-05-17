import numpy as np
import pandas as pd
import pdpipe as pdp
import matplotlib.pyplot as plt
import glob
import os
import csv
from itertools import islice
from decimal import Decimal
import xml.etree.ElementTree as et
from xml.etree.ElementTree import parse
import openpyxl
import pytest
from datetime import datetime


# from main import *


# Update prep list with manually adjusted uom
def update_uom_for_preps(manual_prep, preps):
    for index, row in manual_prep.iterrows():
        PrepId = manual_prep.loc[index, "PrepId"]
        qty = manual_prep.loc[index, "StdQty"]
        uom = manual_prep.loc[index, "StdUom"]
        preps.loc[preps["PrepId"] == PrepId, "StdQty"] = qty
        preps.loc[preps["PrepId"] == PrepId, "StdUom"] = uom
    return preps


def import_list_of_new_items_with_emission_factors(items_assigned, new_items_added):
    # combine the assigned items and newly added items into one DataFrame
    frames = [items_assigned, new_items_added]
    # concatenate the DataFrames and reset the index and drop duplicates
    items_assigned_updated = pd.concat(frames).reset_index(drop=True, inplace=False).drop_duplicates()
    # convert the "CategoryID" column to a numeric data type
    items_assigned_updated[["CategoryID"]] = items_assigned_updated[["CategoryID"]].apply(pd.to_numeric)
    # return the updated DataFrame
    return items_assigned_updated


def map_items_to_ghge_factors(items_assigned_updated, ghge_factors):
    # merge items_assigned_updated and ghge_factors dataframes on 3 columns listed below
    mapping = pd.merge(items_assigned_updated, ghge_factors.loc[:, ["Category ID", "Food Category",
                                                                    "Active Total Supply Chain Emissions (kg CO2 / kg "
                                                                    "food)"]],
                       how="left", left_on="CategoryID", right_on="Category ID")
    # loop through the rows of the mapping dataframe and set Active Total Supply Chain Emissions (kg CO2 / kg food)
    # to 0 if the Category ID is NaN
    for index in mapping.index:
        if np.isnan(mapping.loc[index, "Category ID"]):
            mapping.loc[index, "Active Total Supply Chain Emissions (kg CO2 / kg food)"] = 0
    # drop the columns Category ID and Food Category
    mapping = mapping.drop(columns=["Category ID", "Food Category"])
    # return the updated mapping dataframe
    return mapping


def map_items_to_nitrogen_factors(mapping, nitro_factors):
    # merge mapping and nitro_factors dataframes on 3 columns listed below
    mapping = pd.merge(mapping, nitro_factors.loc[:, ["Category ID", "Food Category", "g N lost/kg product"]],
                       how="left", left_on="CategoryID", right_on="Category ID")
    # loop through the rows of the mapping dataframe and set "g N lost/kg product" to 0 if the Category ID is NaN
    for index in mapping.index:
        if np.isnan(mapping.loc[index, "Category ID"]):
            mapping.loc[index, "g N lost/kg product"] = 0
    # drop the columns Category ID and Food Category
    mapping = mapping.drop(columns=["Category ID", "Food Category"])
    # return the updated mapping dataframe
    return mapping


def map_items_to_water_factors(mapping, water_factors):
    # merge mapping with water_factors DataFrame on 4 columns listed below
    mapping = pd.merge(mapping, water_factors.loc[:, ["Category ID", "Food Category",
                                                      "Freshwater Withdrawals (L/FU)",
                                                      "Stress-Weighted Water Use (L/FU)"]],
                       how="left", left_on="CategoryID", right_on="Category ID")
    # loop through the rows of the mapping dataframe and set "Freshwater Withdrawals (L/FU)" to 0 and set
    # "Stress-Weighted Water Use (L/FU)" to 0 if the Category ID is NaN
    for index in mapping.index:
        if np.isnan(mapping.loc[index, "Category ID"]):
            mapping.loc[index, "Freshwater Withdrawals (L/FU)"] = 0
            mapping.loc[index, "Stress-Weighted Water Use (L/FU)"] = 0
    # drop Category ID and Food Category columns from the mapping DataFrame and return it
    mapping = mapping.drop(columns=["Category ID", "Food Category"])
    return mapping


# most recently added function below
def map_items_to_land_factors(mapping, land_factors):
    # merge mapping with land_factors DataFrame on 3 columns listed below
    mapping = pd.merge(mapping, land_factors.loc[:, ["Category ID", "Food Category",
                                                     "km^2 land use/kg product"]],
                       how="left", left_on="CategoryID", right_on="Category ID")
    # loop through the rows of the mapping dataframe and set "km^2 land use/kg product" to 0 if the Category ID is NaN
    for index in mapping.index:
        if np.isnan(mapping.loc[index, "Category ID"]):
            mapping.loc[index, "km^2 land use/kg product"] = 0
    # drop Category ID and Food Category columns from the mapping DataFrame and return it
    mapping = mapping.drop(columns=["Category ID", "Food Category"])
    return mapping


def manual_adjust_factors(manual_factor, mapping):
    # iterate through each row of manual_factor dataframe
    for index, row in manual_factor.iterrows():
        # get the itemId, ghge, nitro, water, and stress-weighted water values from the current row
        itemId = manual_factor.loc[index, "ItemId"]
        ghge = manual_factor.loc[index, "Active Total Supply Chain Emissions (kg CO2 / kg food)"]
        nitro = manual_factor.loc[index, "g N lost/kg product"]
        water = manual_factor.loc[index, "Freshwater Withdrawals (L/FU)"]
        str_water = manual_factor.loc[index, "Stress-Weighted Water Use (L/FU)"]

        # most recently added
        land = manual_factor.loc[index, "km^2 land use/kg product"]
        # update the corresponding values in the mapping dataframe for the current ItemId
        mapping.loc[mapping['ItemId'] == itemId, 'Active Total Supply Chain Emissions (kg CO2 / kg food)'] = ghge
        mapping.loc[mapping['ItemId'] == itemId, 'g N lost/kg product'] = nitro
        mapping.loc[mapping['ItemId'] == itemId, 'Freshwater Withdrawals (L/FU)'] = water
        mapping.loc[mapping['ItemId'] == itemId, 'Stress-Weighted Water Use (L/FU)'] = str_water

        # most recently added
        mapping.loc[mapping['ItemId'] == itemId, 'km^2 land use/kg product'] = land
    # drop any duplicate rows based on the ItemId column
    # mapping.drop_duplicates(subset=["ItemId"], inplace=True)

    # return the updated mapping dataframe
    return mapping

    # common way to ensure that code inside this block is only executed if the script is run directly
    # allows a Python file to be used as a module and a standalone program which can be run from cmd or terminal
    # here block is empty so if the script is run directly, nothing will happen. The script is designed to be used as a
    # module, providing functions that can be used in other scripts or programs.


if __name__ == '__main__':
    pass
