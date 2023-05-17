import pandas as pd
import os
import glob
import xml.etree.ElementTree as et

path = "C:/Users/smvan/CFFS-S23/CFFS-22-23"
os.chdir(path)

# joins the main path with data/raw/Gather 22-23.oc files
filepath_list = glob.glob(os.path.join(os.getcwd(), "data", "raw", "Gather 22-23*", "*.oc"))


def import_items_list(Items_name):

    # empty lists for all items ids, and other attributes
    ItemId = []
    Description = []
    CaseQty = []
    CaseUOM = []
    PakQty = []
    PakUOM = []
    InventoryGroup = []

    # gets data from XML files and add them to lists and then create dataframe with it.
    for filepath in filepath_list:
        path = filepath + f'/{Items_name}.xml'
        if os.path.isfile(path):
            xtree = et.parse(path)
            xroot = xtree.getroot()
            for item in xtree.iterfind('Item'):
                ItemId.append(item.attrib['id'])
                Description.append(item.findtext('Description'))
                CaseQty.append(item.findtext('CaseQty'))
                CaseUOM.append(item.findtext('CaseUOM'))
                PakQty.append(item.findtext('PakQty'))
                PakUOM.append(item.findtext('PakUOM'))
                InventoryGroup.append(item.findtext('InventoryGroup'))

    Items = pd.DataFrame({'ItemId': ItemId, 'Description': Description, 'CaseQty': CaseQty,
                          'CaseUOM': CaseUOM, 'PakQty': PakQty, 'PakUOM': PakUOM, 'InventoryGroup': InventoryGroup}
                         ).drop_duplicates()

    Items.reset_index(drop=True, inplace=True)

    path = os.path.join(os.getcwd(), "data", "preprocessed", f"{Items_name}_List.csv")
    Items.to_csv(path, index=False, header=True)
    return Items


def import_ingredients_list(Ingredients_name):
    IngredientId = []
    Conversion = []
    InvFactor = []
    Qty = []
    Recipe = []
    Uom = []

    # gets data from XML files and add them to lists and then create dataframe with it.

    for filepath in filepath_list:
        path = filepath + f'/{Ingredients_name}.xml'
        if os.path.isfile(path):
            xtree = et.parse(path)
            xroot = xtree.getroot()
            for x in xtree.iterfind('Ingredient'):
                IngredientId.append(x.attrib['ingredient'])
                Conversion.append(x.attrib['conversion'])
                InvFactor.append(x.attrib['invFactor'])
                Qty.append(x.attrib['qty'])
                Recipe.append(x.attrib['recipe'])
                Uom.append(x.attrib['uom'])

    Ingredients = pd.DataFrame({'IngredientId': IngredientId, 'Qty': Qty, 'Uom': Uom, 'Conversion': Conversion,
                                'InvFactor': InvFactor, 'Recipe': Recipe}).drop_duplicates()

    Ingredients.reset_index(drop=True, inplace=True)

    path = os.path.join(os.getcwd(), "data", "preprocessed", f"{Ingredients_name}_List.csv")
    Ingredients.to_csv(path, index=False, header=True)
    return Ingredients


def import_preps_list(Preps_name):
    PrepId = []
    Description = []
    PakQty = []
    PakUOM = []
    InventoryGroup = []

    # gets data from XML files and add them to lists and then create dataframe with it.

    for filepath in filepath_list:
        path = filepath + f'/{Preps_name}.xml'
        if os.path.isfile(path):
            xtree = et.parse(path)
            xroot = xtree.getroot()
            for x in xtree.iterfind('Prep'):
                PrepId.append(x.attrib['id'])
                Description.append(x.findtext('Description'))
                PakQty.append(x.findtext('PakQty'))
                PakUOM.append(x.findtext('PakUOM'))
                InventoryGroup.append(x.findtext('InventoryGroup'))

    Preps = pd.DataFrame({'PrepId': PrepId, 'Description': Description,
                          'PakQty': PakQty, 'PakUOM': PakUOM, 'InventoryGroup': InventoryGroup}).drop_duplicates()

    Preps.reset_index(drop=True, inplace=True)

    path = os.path.join(os.getcwd(), "data", "preprocessed", f"{Preps_name}_List.csv")
    Preps.to_csv(path, index=False, header=True)
    return Preps


def import_products_list(Products_name):
    ProdId = []
    Description = []
    SalesGroup = []

    # gets data from XML files and add them to lists and then create dataframe with it.

    for filepath in filepath_list:
        path = filepath + f'/{Products_name}.xml'
        if os.path.isfile(path):
            xtree = et.parse(path)
            xroot = xtree.getroot()
            for x in xtree.iterfind('Prod'):
                ProdId.append(x.attrib['id'])
                Description.append(x.findtext('Description'))
                SalesGroup.append(x.findtext('SalesGroup'))

    Products = pd.DataFrame({'ProdId': ProdId, 'Description': Description, 'SalesGroup': SalesGroup}).drop_duplicates()

    Products.reset_index(drop=True, inplace=True)
    Products.drop_duplicates(subset=["ProdId"], inplace=True)

    path = os.path.join(os.getcwd(), "data", "preprocessed", f"{Products_name}_List.csv")
    Products.to_csv(path, index=False, header=True)
    return Products


def import_conversions_list(Conversions_name):
    ConversionId = []
    Multiplier = []
    ConvertFromQty = []
    ConvertFromUom = []
    ConvertToQty = []
    ConvertToUom = []

    # gets data from XML files and add them to lists and then create a dataframe with it.

    for filepath in filepath_list:
        path = filepath + f'/{Conversions_name}.xml'
        if os.path.isfile(path):
            xtree = et.parse(path)
            xroot = xtree.getroot()
            for x in xtree.iterfind('Conversion'):
                ConversionId.append(x.attrib['id'])
                Multiplier.append(x.attrib['multiplier'])
                ConvertFromQty.append(x.find('ConvertFrom').attrib['qty'])
                ConvertFromUom.append(x.find('ConvertFrom').attrib['uom'])
                ConvertToQty.append(x.find('ConvertTo').attrib['qty'])
                ConvertToUom.append(x.find('ConvertTo').attrib['uom'])

    Conversions = pd.DataFrame(
        {'ConversionId': ConversionId, 'Multiplier': Multiplier, 'ConvertFromQty': ConvertFromQty,
         'ConvertFromUom': ConvertFromUom, 'ConvertToQty': ConvertToQty, 'ConvertToUom': ConvertToUom}
    ).drop_duplicates()

    Conversions.reset_index(drop=True, inplace=True)

    path = os.path.join(os.getcwd(), "data", "preprocessed", f"{Conversions_name}_List.csv")
    Conversions.to_csv(path, index=False, header=True)
    return Conversions


if __name__ == '__main__':
    pass
