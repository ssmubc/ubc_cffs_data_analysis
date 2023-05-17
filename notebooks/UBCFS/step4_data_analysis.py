import pandas as pd
from notebooks.UBCFS.step2_data_cleaning import spc_converter, std_converter


def unit_conversion_for_preps(manual_prepu, conversions):
    # select the columns of interest
    prep_cov = manual_prepu[["PrepId", "PakQty", "PakUOM", "StdQty", "StdUom"]]
    # insert a new column "Multiplier" and rename columns to match conversions dataframe
    prep_cov.insert(1, "Multiplier", "")
    prep_cov.columns = conversions.columns
    # calculate conversion factor and store it in the "Multiplier" column
    for ind, row in prep_cov.iterrows():
        prep_cov.loc[ind, "Multiplier"] = float(row["ConvertFromQty"]) / float(row["ConvertToQty"])
    # prep_cov.loc['Multiplier'] = prep_cov['ConvertFromQty'] / prep_cov['ConvertToQty']
    # concatenate the 2 dataframes, drop duplicates, and return resulting dataframe: conversions
    frames = [conversions, prep_cov]
    conversions = pd.concat(frames).reset_index(drop=True, inplace=False).drop_duplicates()
    return conversions


def rearrange_preps(preps):
    # create new columns with emission factors and have all their values to be 0
    preps["GHG Emission (g)"] = 0
    preps["GHG Emission (g)/StdUom"] = 0
    preps["N lost (g)"] = 0
    preps["N lost (g)/StdUom"] = 0
    preps["Freshwater Withdrawals (ml)"] = 0
    preps["Freshwater Withdrawals (ml)/StdUom"] = 0
    preps["Stress-Weighted Water Use (ml)"] = 0
    preps["Stress-Weighted Water Use (ml)/StdUom"] = 0

    # most recently added
    preps["km^2 land use/kg product"] = 0
    preps["km^2 land use/kg product/StdUom"] = 0
    return preps


def get_items_ghge_prep(index, row, ingredient, preps, mapping, spc_cov, conversions, liquid_unit, solid_unit,
                        std_unit):
    ingres = ingredient.loc[ingredient["Recipe"] == preps.loc[index, "PrepId"]]
    # initialize variables for GHG emissions, nitrogen lost, water usage, and meal weight
    ghg = preps.loc[index, "GHG Emission (g)"]
    nitro = preps.loc[index, "N lost (g)"]
    water = preps.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = preps.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = preps.loc[index, "StdQty"]

    # most recently added
    land = preps.loc[index, "km^2 land use/kg product"]
    # loop through each ingredient in the recipe
    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        # check if ingredient is a food item
        if ingre.startswith("I"):
            # get the GHG emission, nitrogen lost, and water usage factors for the ingredient
            ghge = mapping.loc[mapping["ItemId"] == ingre, "Active Total Supply Chain Emissions (kg CO2 / kg food)"]
            nitro_fac = mapping.loc[mapping["ItemId"] == ingre, "g N lost/kg product"]
            water_fac = mapping.loc[mapping["ItemId"] == ingre, "Freshwater Withdrawals (L/FU)"]
            str_water_fac = mapping.loc[mapping["ItemId"] == ingre, "Stress-Weighted Water Use (L/FU)"]

            # most recently added
            land_fac = mapping.loc[mapping["ItemId"] == ingre, "km^2 land use/kg product"]

            # get the quantity and unit of measurement for the ingredient
            Qty = float(ingres.loc[ind, "Qty"])
            Uom = ingres.loc[ind, "Uom"]
            # check if the ingredient has a specific conversion factor
            if ingre in spc_cov:
                # convert the ingredient quantity to standard unit and calculate the GHG emissions, nitrogen lost,
                # and water usage
                qty = spc_converter(ingre, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac) / 1000
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)

                # most recently added
                land += qty * float(land_fac)

            else:
                # convert the ingredient quantity to standard unit and calculate the GHG emissions, nitrogen lost,
                # and water usage
                qty = std_converter(Qty, Uom, std_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac) / 1000
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)

                # most recently added
                land += qty * float(land_fac)
    # update the recipe GHG emissions, nitrogen lost, and water usage
    preps.loc[index, "GHG Emission (g)"] = float(ghg)
    preps.loc[index, "GHG Emission (g)/StdUom"] = ghg / float(weight)
    preps.loc[index, "N lost (g)"] = float(nitro)
    preps.loc[index, "N lost (g)/StdUom"] = nitro / float(weight)
    preps.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    preps.loc[index, 'Freshwater Withdrawals (ml)/StdUom'] = water / float(weight)
    preps.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)
    preps.loc[index, 'Stress-Weighted Water Use (ml)/StdUom'] = str_water / float(weight)

    # most recently added
    preps.loc[index, 'km^2 land use/kg product'] = float(land)
    preps.loc[index, 'km^2 land use/kg product/StdUom'] = land / float(weight)
    return preps


def link_preps(index, row, ingredients, preps, spc_cov, conversions, liquid_unit, solid_unit, std_unit):
    ingres = ingredients.loc[ingredients["Recipe"] == preps.loc[index, "PrepId"]]
    ghg = preps.loc[index, "GHG Emission (g)"]
    nitro = preps.loc[index, "N lost (g)"]
    water = preps.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = preps.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = preps.loc[index, "StdQty"]

    # most recently added
    land = preps.loc[index, 'km^2 land use/kg product']
    # checks if length of ingredients with ingredients in the recipe equal to the ingredients in preps is 1
    if len(ingres) == 1:
        ingre = ingres.iloc[0]["IngredientId"]
        # checks if the ingredient is a prep item
        if ingre.startswith("P"):
            ghge = preps.loc[preps["PrepId"] == ingre, "GHG Emission (g)/StdUom"]
            nitro_fac = preps.loc[preps["PrepId"] == ingre, "N lost (g)/StdUom"]
            water_fac = preps.loc[preps["PrepId"] == ingre, "Freshwater Withdrawals (ml)/StdUom"]
            str_water_fac = preps.loc[preps["PrepId"] == ingre, "Stress-Weighted Water Use (ml)/StdUom"]

            # most recently added
            land_fac = preps.loc[preps['PrepId'] == ingre, "km^2 land use/kg product/StdUom"]

            Qty = float(ingres.iloc[0]["Qty"])
            Uom = ingres.iloc[0]["Uom"]
            if ingre in spc_cov:
                qty = spc_converter(ingre, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)

                # most recently added
                land += qty * float(land_fac)
            else:
                qty = std_converter(Qty, Uom, std_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)

                # most recently added
                land += qty * float(land_fac)

    # update values in preps
    preps.loc[index, "GHG Emission (g)"] = float(ghg)
    preps.loc[index, "GHG Emission (g)/StdUom"] = ghg / float(weight)
    preps.loc[index, "N lost (g)"] = float(nitro)
    preps.loc[index, "N lost (g)/StdUom"] = nitro / float(weight)
    preps.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    preps.loc[index, 'Freshwater Withdrawals (ml)/StdUom'] = water / float(weight)
    preps.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)
    preps.loc[index, 'Stress-Weighted Water Use (ml)/StdUom'] = str_water / float(weight)

    # most recently added
    preps.loc[index, 'km^2 land use/kg product'] = float(land)
    preps.loc[index, 'km^2 land use/kg product/StdUom'] = land / float(weight)

    return preps


def get_preps_ghge_prep(index, row, ingredients, preps, spc_cov, conversions, liquid_unit, solid_unit, std_unit):
    ingres = ingredients.loc[ingredients["Recipe"] == preps.loc[index, "PrepId"]]
    ghg = preps.loc[index, "GHG Emission (g)"]
    nitro = preps.loc[index, "N lost (g)"]
    water = preps.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = preps.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = preps.loc[index, "StdQty"]

    # most recently added
    land = preps.loc[index, 'km^2 land use/kg product']

    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        # check if ingredient is a prep item and that the length of ingredient is greater than 1
        if ingre.startswith("P") and len(ingres) > 1:
            ghge = preps.loc[preps["PrepId"] == ingre, "GHG Emission (g)/StdUom"]
            nitro_fac = preps.loc[preps["PrepId"] == ingre, "N lost (g)/StdUom"]
            water_fac = preps.loc[preps["PrepId"] == ingre, "Freshwater Withdrawals (ml)/StdUom"]
            str_water_fac = preps.loc[preps["PrepId"] == ingre, "Stress-Weighted Water Use (ml)/StdUom"]

            land_fac = preps.loc[preps['PrepId'] == ingre, 'km^2 land use/kg product/StdUom']
            Qty = float(ingres.loc[ind, "Qty"])
            Uom = ingres.loc[ind, "Uom"]
            if ingre in spc_cov:
                qty = spc_converter(ingre, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)

                # most recently added
                land += qty * float(land_fac)
            else:
                qty = std_converter(Qty, Uom, std_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)

                # most recently added
                land += qty * float(land_fac)
    # update preps
    preps.loc[index, "GHG Emission (g)"] = float(ghg)
    preps.loc[index, "GHG Emission (g)/StdUom"] = ghg / float(weight)
    preps.loc[index, "N lost (g)"] = float(nitro)
    preps.loc[index, "N lost (g)/StdUom"] = nitro / float(weight)
    preps.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    preps.loc[index, 'Freshwater Withdrawals (ml)/StdUom'] = water / float(weight)
    preps.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)
    preps.loc[index, 'Stress-Weighted Water Use (ml)/StdUom'] = str_water / float(weight)

    # most recently added
    preps.loc[index, 'km^2 land use/kg product'] = float(land)
    preps.loc[index, 'km^2 land use/kg product/StdUom'] = land / float(weight)

    return preps


def rearrange_products(products):
    # create columns with environmental factors and set their initial values to be 0.
    products['Weight (g)'] = 0
    products['GHG Emission (g)'] = 0
    products['N lost (g)'] = 0
    products['Freshwater Withdrawals (ml)'] = 0
    products['Stress-Weighted Water Use (ml)'] = 0

    # most recently added
    products['km^2 land use/kg product'] = 0
    return products


def get_items_ghge(index, row, ingredient, products, mapping, conversions, liquid_unit, solid_unit, std_unit):
    ingres = ingredient.loc[ingredient["Recipe"] == products.loc[index, "ProdId"]]
    ghg = products.loc[index, "GHG Emission (g)"]
    nitro = products.loc[index, "N lost (g)"]
    water = products.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = products.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = products.loc[index, "Weight (g)"]

    # most recently added
    land = products.loc[index, "km^2 land use/kg product"]

    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        if ingre.startswith("I"):
            ghge = mapping.loc[mapping["ItemId"] == ingre, "Active Total Supply Chain Emissions (kg CO2 / kg food)"]
            nitro_fac = mapping.loc[mapping["ItemId"] == ingre, "g N lost/kg product"]
            water_fac = mapping.loc[mapping["ItemId"] == ingre, "Freshwater Withdrawals (L/FU)"]
            str_water_fac = mapping.loc[mapping["ItemId"] == ingre, "Stress-Weighted Water Use (L/FU)"]

            # most recently added
            land_fac = mapping.loc[mapping["ItemId"] == ingre, "km^2 land use/kg product"]

            Qty = float(ingres.loc[ind, "Qty"])
            Uom = ingres.loc[ind, "Uom"]
            if ingre in conversions["ConversionId"].tolist():
                qty = spc_converter(ingre, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
                weight += qty
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac) / 1000
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)

                # most recently added
                land += qty * float(land_fac)
            else:
                qty = std_converter(Qty, Uom, std_unit)[0]
                weight += qty
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac) / 1000
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)

                # most recently added
                land += qty * float(land_fac)

    products.loc[index, "GHG Emission (g)"] = float(ghg)
    products.loc[index, "Weight (g)"] = float(weight)
    products.loc[index, "N lost (g)"] = float(nitro)
    products.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    products.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)

    # most recently added
    products.loc[index, 'km^2 land use/kg product'] = float(land)
    return products


def spc_converter(ingre, qty, uom, conversions, liquid_unit, solid_unit):
    """
    If the unit can be converted to standard units (g or ml), directs to std_converter.
    If ingre(IngredientId) is in spc_cov, find conversionId, converting unit, conversion unit from
    `data/cleaning/Conversions_Added.csv`.
    """

    spc_cov = list(filter(None, conversions["ConversionId"].tolist()))

    if uom in liquid_unit + solid_unit:
        return std_converter(qty, uom)
    elif ingre in spc_cov:
        conversion = conversions.loc[(conversions["ConversionId"] == ingre) &
                                     (conversions["ConvertFromUom"] == uom) &
                                     (conversions["ConvertToUom"] == "g")]
        # conversion = conversion.replace(r'^\s*$', np.nan, regex=True)
        conversion.drop_duplicates(subset=['ConversionId'], inplace=True)
        multiplier = conversion["Multiplier"]
        if multiplier.empty:
            return std_converter(qty, uom)
        else:
            Qty = float(qty) / float(multiplier)
            Uom = conversion["ConvertToUom"].values[0]
            return (Qty, Uom)
    else:
        return std_converter(qty, uom)


def get_preps_ghge(index, row, ingredient, products, preps, conversions, liquid_unit, solid_unit, std_unit):
    ingres = ingredient.loc[ingredient["Recipe"] == products.loc[index, "ProdId"]]
    ghg = products.loc[index, "GHG Emission (g)"]
    nitro = products.loc[index, "N lost (g)"]
    water = products.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = products.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = products.loc[index, "Weight (g)"]

    # most recently added
    land = products.loc[index, "km^2 land use/kg product"]

    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        # checks if the ingredient starts with P
        if ingre.startswith("P"):
            ghge = preps.loc[preps["PrepId"] == ingre, "GHG Emission (g)/StdUom"]
            nitro_fac = preps.loc[preps["PrepId"] == ingre, "N lost (g)/StdUom"]
            water_fac = preps.loc[preps["PrepId"] == ingre, "Freshwater Withdrawals (ml)/StdUom"]
            str_water_fac = preps.loc[preps["PrepId"] == ingre, "Stress-Weighted Water Use (ml)/StdUom"]

            # most recently added
            land_fac = preps.loc[preps["PrepId"] == ingre, "km^2 land use/kg product/StdUom"]
            Qty = float(ingres.loc[ind, "Qty"])
            # get the unit of measurement for all ingredients (ind)
            Uom = ingres.loc[ind, "Uom"]
            # check if ingredient is in conversions['ConversionId']
            if ingre in conversions["ConversionId"].tolist():
                qty = spc_converter(ingre, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
                weight += qty
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)

                # most recently added
                land += qty * float(land_fac)
            else:
                qty = std_converter(Qty, Uom, std_unit)[0]
                weight += qty
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)

                # most recently added
                land += qty * float(land_fac)

    # adjust the products dataframe and return it
    products.loc[index, "GHG Emission (g)"] = float(ghg)
    products.loc[index, "Weight (g)"] = float(weight)
    products.loc[index, "N lost (g)"] = float(nitro)
    products.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    products.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)

    # most recently added
    products.loc[index, 'km^2 land use/kg product'] = float(land)

    return products


def get_products_ghge(index, row, ingredient, products):
    ingres = ingredient.loc[ingredient["Recipe"] == products.loc[index, "ProdId"]]
    # get the values of environmental factors and add them to the vectors
    ghg = products.loc[index, "GHG Emission (g)"]
    nitro = products.loc[index, "N lost (g)"]
    water = products.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = products.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = products.loc[index, "Weight (g)"]

    # most recently added
    land = products.loc[index, 'km^2 land use/kg product']

    # iterate through the rows and grab the indexes
    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        # check if the ingredient starts with R
        if ingre.startswith("R"):
            ghge = products.loc[products["ProdId"] == ingre, "GHG Emission (g)"]
            nitro_fac = products.loc[products["ProdId"] == ingre, "N lost (g)"]
            water_fac = products.loc[products["ProdId"] == ingre, "Freshwater Withdrawals (ml)"]
            str_water_fac = products.loc[products["ProdId"] == ingre, "Stress-Weighted Water Use (ml)"]

            # most recently added
            land_fac = products.loc[products["ProdId"] == ingre, "km^2 land use/kg product"]

            Weight = products.loc[products["ProdId"] == ingre, "Weight (g)"]
            Qty = float(ingres.loc[ind, "Qty"])
            ghg += Qty * float(ghge)
            nitro += Qty * float(nitro_fac)
            water += Qty * float(water_fac)
            str_water += Qty * float(str_water_fac)
            weight += Qty * float(Weight)

            # most recently added
            land += Qty * float(land_fac)
    # modify products and return it
    products.loc[index, "GHG Emission (g)"] = float(ghg)
    products.loc[index, "Weight (g)"] = float(weight)
    products.loc[index, "N lost (g)"] = float(nitro)
    products.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    products.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)

    # most recently added
    products.loc[index, 'km^2 land use/kg product'] = float(land)
    return products


def filter_products(index, row, ingredients, preps_nonstd, products):
    # select ingredients for specific product
    ingres = ingredients.loc[ingredients["Recipe"] == products.loc[index, "ProdId"]]

    # iterate over the ingredients
    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]

        # check if the ingredient is in the non-standard preparations
        if ingre in preps_nonstd["PrepId"].tolist():
            # print info
            print(ingre, index, products.loc[index, "ProdId"])
            # remove the product from the products dataframe if it is in the non-standard preparation
            products.drop(index, inplace=True)

            # This function removes products from the dataframe if they contain any
            # ingredients that are part of the non-standard preparations.
            break


def products_cleanup(products):
    # convert freshwater withdrawals and stress-weighted water from mL to L and round to 2 decimal places
    products['Freshwater Withdrawals (L)'] = round(products['Freshwater Withdrawals (ml)'] / 1000, 2)
    products['Stress-Weighted Water Use (L)'] = round(products['Stress-Weighted Water Use (ml)'] / 1000, 2)

    # drop original columns for freshwater withdrawals and stress-weighted water use in mL
    products = products.drop(columns=['Freshwater Withdrawals (ml)', 'Stress-Weighted Water Use (ml)'])

    # calculate GHG emission, nitrogen loss, freshwater withdrawals, and stress-weighted water use per 100 grams of
    # weight
    products['GHG Emission (g) / 100g'] = round(100 * products['GHG Emission (g)'] / products['Weight (g)'], 2)
    products['N lost (g) / 100g'] = round(100 * products['N lost (g)'] / products['Weight (g)'], 2)
    products['Freshwater Withdrawals (L) / 100g'] = round(
        100 * products['Freshwater Withdrawals (L)'] / products['Weight (g)'], 2)
    products['Stress-Weighted Water Use (L) / 100g'] = round(
        100 * products['Stress-Weighted Water Use (L)'] / products['Weight (g)'], 2)

    # most recently added
    products['km^2 land use/kg product / 100g'] = round(
        100 * products['km^2 land use/kg product'] / products['Weight (g)'], 2)

    # print the updated products dataframe and return it
    print(products)
    return products
