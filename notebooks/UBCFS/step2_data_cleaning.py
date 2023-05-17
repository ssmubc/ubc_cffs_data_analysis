import numpy as np
import pandas as pd

Std_Unit = pd.read_csv("C:/Users/smvan/CFFS-S23/CFFS-22-23/data/external/standard_conversions.csv")


def update_conversions_list(update_conv, conversions):
    """
    Updates `data/cleaning/update/Conv_UpdateConv.csv`.
    """

    # retrieves the value in the 'ConversionId' column using Update_Conv.loc[index, 'ConversionId']
    # and assigns it to the variable Id.

    # row: a Series (1-d array in pandas) You can access the individual values of the row using the column headers as
    # keys to the
    # like row['column_name'].

    # if the IDs of Update_Conv are the same IDs as Conversions then we drop it from the Conversions dataframe

    for index, row in update_conv.iterrows():
        Id = update_conv.loc[index, 'ConversionId']
        conversions.drop(conversions[conversions['ConversionId'] == Id].index, inplace=True)

    # combine two data frames, reset the index and remove any duplicates in the concatenated data frame,
    # and return the resulting data frame.

    # Added comments below on May 8th

    # frames variable is created as a list of two DataFrames, Conversions and Update_Conv.
    # pd.concat() function is used to concatenate the two DataFrames vertically (i.e., stack one on top of the other).

    # drop_duplicates() method is used to remove any duplicate rows from the concatenated DataFrame based on all
    # columns. The resulting DataFrame has only unique rows.

    # The resulting DataFrame is assigned back to the variable Conversions,

    # drop = True ensures that the old index is not added as a new column to the dataframe
    # inplace=False parameter ensures that a new DataFrame is returned rather than modifying
    # the original Conversions DataFrame in place.

    frames = [conversions, update_conv]
    conversions = pd.concat(frames).reset_index(drop=True, inplace=False).drop_duplicates()
    return conversions

    # takes a data frame and assigns a new column called Multiplier to the dataframe uses iterrows() to iterate through
    # the rows.Then subset_conv will have a new column named Multiplier with the computed values.


def assign_multiplier(update_conv):
    for ind, row in update_conv.iterrows():
        if pd.isnull(row["Multiplier"]):
            update_conv.loc[ind, "Multiplier"] = row["ConvertFromQty"] / row["ConvertToQty"]
    return update_conv

    # Seperate uoms that converted to 'ml' or 'g'
    # Below we create 2 lists.
    # list_unit contains list of unit of measurements that are being converted to milliliters
    # solid_unit contains a list of unit of measurements that are being converted to grams
    # tolist() converts a Pandas Series or an array to a python list.


def sort_liquid_and_solid_unit(std_unit):
    """
    Identifies items in `data/external/standard_conversions.csv` that converts TO g or ml.
    """

    liquid_unit = std_unit.loc[std_unit['ConvertToUom'] == 'ml', 'ConvertFromUom'].tolist()
    solid_unit = std_unit.loc[std_unit['ConvertToUom'] == 'g', 'ConvertFromUom'].tolist()
    return liquid_unit, solid_unit


# Classifies whether the given unit is in standard unit list.
# If the unit is found, returns quantity and unit being converted to.
# If the unit is not present in `data/external/standard_conversions.csv`, returns original quantity and uom.
def std_converter(qty, uom, std_unit=Std_Unit):
    # std_unit = pd.read_csv("data/external/standard_conversions.csv")

    """
    From `data/external/standard_conversions.csv`, if the unit is defined under "ConvertFromUom",
    returns converted quantity and new unit of measurement.
    If not found in `data/external/standard_conversions.csv`, returns quantity and original unit.
    """

    if uom in std_unit["ConvertFromUom"].tolist():
        multiplier = std_unit.loc[std_unit["ConvertFromUom"] == uom, "Multiplier"]
        Qty = float(qty) * float(multiplier)
        Uom = std_unit.loc[std_unit["ConvertFromUom"] == uom, "ConvertToUom"].values[0]
    else:
        Qty = qty
        Uom = uom
    return (Qty, Uom)


def spc_converter(ingre, qty, uom, conversions, liquid_unit, solid_unit):
    """
    If the unit can be converted to standard units (g or ml), directs to std_converter.
    If ingre(IngredientId) is in spc_cov, find conversionId, converting unit, conversion unit from
    `data/cleaning/Conversions_Added.csv`.
    """
    # After this line below, spc_cov contains only the non-empty values from the 'ConversionId' column of the
    # Conversions DataFrame.
    spc_cov = list(filter(None, conversions["ConversionId"].tolist()))
    # spc_cov = [item for item in spc_cov if not (pd.null(item)) == True]

    # Comments for spc_converter:
    # The function checks if ingredient is in the liquid_unit or solid_unit lists. If so, it calls std_converter(qty,
    # uom) to convert the quantity and UOM to a standardized unit.

    # If uom is not in liquid_unit or solid_unit it checks if ingre is in spc_cov, if it is and the ConvertToUom is
    # equal to grams then the function applies the factor to the qty argument to convert it to the standardized unit,
    # and returns the result as a tuple containing the converted quantity and uom. If no conversion found, then it
    # calls std_converter(qty, uom)

    # If uom not in liquid_unit or solid_unit and if ingre is not in spc_cov then the function calls
    # std_converter(qty, uom)
    if uom in liquid_unit + solid_unit:
        return std_converter(qty, uom)
    elif ingre in spc_cov:
        conversion = conversions.loc[(conversions["ConversionId"] == ingre) &
                                     (conversions["ConvertFromUom"] == uom) &
                                     (conversions["ConvertToUom"] == "g")]
        # conversion.drop_duplicates(subset=['ConversionId'], inplace=True)
        multiplier = conversion["Multiplier"]
        if multiplier.empty:
            return std_converter(qty, uom)
        else:
            Qty = float(qty) / float(multiplier)
            Uom = conversion["ConvertToUom"].values[0]
            return (Qty, Uom)
    else:
        return std_converter(qty, uom)


# Filter out items with unit information unknown
def items_with_nonstd_units(ingre, liquid_unit, solid_unit, conversions):
    # We find the column names
    col_names = list(ingre.columns.values)
    # Create a Items_Nonstd list
    Items_Nonstd = []

    # If the unit of measurement is not grams or ml and ingredient id starts with I and the ingredient is not in
    # ConversionId column of Conversions then we add it to Items_Nonstd list
    for ind, row in ingre.iterrows():
        Ingre = ingre.loc[ind, "IngredientId"]
        Uom = ingre.loc[ind, "Uom"]
        if Uom not in ["g", "ml"] and Uom not in liquid_unit + solid_unit and Ingre.startswith("I") and Ingre not in \
                conversions["ConversionId"].tolist():
            Dict = {}
            Dict.update(dict(row))
            Items_Nonstd.append(Dict)
    # Create a DataFrame from Items_Nonstd list
    Items_Nonstd = pd.DataFrame(Items_Nonstd, columns=col_names)
    # Remove duplicate ingredients of the same properties so that Items_Nonstd has only unique rows.
    Items_Nonstd.drop_duplicates(subset=["IngredientId"], inplace=True)
    return Items_Nonstd


def cleanup_preps_units(preps, conversions, Std_Unit):
    liquid_unit, solid_unit = sort_liquid_and_solid_unit(Std_Unit)
    # Creates 2 new columns called StdQty and StdUom in the Preps DataFrame. These columns contain NaN values
    # Preparing to fill in these columns with standardized quantities and units of measurement
    preps["StdQty"] = np.nan
    preps["StdUom"] = np.nan
    # Convert uom into 'g' or 'ml' for each prep using the unit converter

    # Retrieve the PrepId, PakQty, and PakUOM from the current row
    # Pass these values to spc_converter, then we update the StdQty and StdUom columns of the current row with the
    # converted values.
    for index in preps.index:
        PrepId = preps.loc[index, "PrepId"]
        Qty = preps.loc[index, "PakQty"]
        Uom = preps.loc[index, "PakUOM"]
        preps.loc[index, "StdQty"] = spc_converter(PrepId, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
        preps.loc[index, "StdUom"] = spc_converter(PrepId, Qty, Uom, conversions, liquid_unit, solid_unit)[1]
    return preps


def preps_with_nonstd_unit(preps):
    # preps: Preps_Unit_Cleaned.csv

    # Find out preps with non-standard units
    col_names = list(preps.columns.values)
    # Create a preps_nonstd list
    preps_nonstd = []

    # If the unit of measurement is not grams or ml then we add the row to preps_nonstd
    for index, row in preps.iterrows():
        StdUom = preps.loc[index, "StdUom"]
        if StdUom not in ["g", "ml"]:
            Dict = {}
            Dict.update(dict(row))
            preps_nonstd.append(Dict)
    # Create a DataFrame preps_nonstd from preps_nonstd list
    preps_nonstd = pd.DataFrame(preps_nonstd, columns=col_names)

    manual_prepU = pd.read_csv("C:/Users/smvan/CFFS-S23/CFFS-22-23/data/cleaning/update/Preps_UpdateUom.csv")
    col_names2 = list(preps_nonstd.columns.values)
    preps_nonstd_na = []

    # if prepId not a value in the manual_prepU column for PrepId values then add it to preps_nonstd_na
    for index, row in preps_nonstd.iterrows():
        PrepId = preps_nonstd.loc[index, "PrepId"]
        if PrepId not in manual_prepU["PrepId"].values:
            Dict = {}
            Dict.update(dict(row))
            preps_nonstd_na.append(Dict)

    preps_nonstd = pd.DataFrame(preps_nonstd_na, columns=col_names2)
    return preps_nonstd


def sort_new_items(items, items_list_assigned):
    col_names = list(items.columns.values)
    # list of new items, new_items_list
    new_items_list = []

    # if the item is not in items_list_assigned.values then append it to the list
    for index, row in items.iterrows():
        ItemId = items.loc[index, "ItemId"]
        if ItemId not in items_list_assigned["ItemId"].values:
            Dict = {}
            Dict.update(dict(row))
            new_items_list.append(Dict)
    # create a dataframe from the list and return it
    new_items_list = pd.DataFrame(new_items_list, columns=col_names)
    return new_items_list


if __name__ == '__main__':
    pass
