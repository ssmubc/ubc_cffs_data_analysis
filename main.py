import os
from notebooks.UBCFS.generate_menu_list import *
from notebooks.UBCFS.step2_data_cleaning import assign_multiplier, update_conversions_list, sort_liquid_and_solid_unit, \
    items_with_nonstd_units, cleanup_preps_units, preps_with_nonstd_unit, sort_new_items
# from notebooks.UBCFS.step2_data_cleaning import *
from notebooks.UBCFS.step3_update_and_mapping import update_uom_for_preps, \
    import_list_of_new_items_with_emission_factors, map_items_to_ghge_factors, map_items_to_water_factors, \
    map_items_to_nitrogen_factors, manual_adjust_factors, map_items_to_land_factors
from notebooks.UBCFS.step4_data_analysis import unit_conversion_for_preps, rearrange_preps, get_items_ghge_prep, \
    link_preps, get_preps_ghge_prep, rearrange_products, get_items_ghge, get_preps_ghge, get_products_ghge, \
    filter_products, products_cleanup
from notebooks.UBCFS.step5_data_labelling import create_visualizations, create_category_true, \
    create_results_all_factors, add_menu_names, create_final_counts, create_ghg_label
from notebooks.UBCFS.step1_data_preprocessing import *

from datetime import datetime

import warnings

path = "C:/Users/smvan/CFFS-S23/CFFS-22-23"
os.chdir(path)

warnings.filterwarnings('ignore')

restaurant_name = "Gather22-23"
print(os.getcwd())

# CFFS Labelling 2022-2023: Jenny Lee
if __name__ == '__main__':

    # Step 1: import all necessary datsta
    print("Step 1: Importing Data begins...")
    items = import_items_list("Items")
    ingredients = import_ingredients_list("Ingredients")
    preps = import_preps_list("Preps")
    products = import_products_list("Products")
    assertpoint = products.shape[0]
    conversions = import_conversions_list("Conversions")

    step1_summary = pd.DataFrame([items.shape, preps.shape, ingredients.shape, products.shape, conversions.shape],
                                 columns=['count', 'columns'], index=['Items', 'Preps', 'Ingredients',
                                                                      'Products', 'Conversions'])
    print(step1_summary)

    # Step 2: data cleaning & preprocessing
    print("\nStep 2: Data and Preprocessing begins...")
    Update_Conv = pd.read_csv("data/cleaning/update/Conv_UpdateConv.csv")
    Update_Conv = assign_multiplier(Update_Conv)
    Update_Conv.to_csv("data/cleaning/update/Conv_UpdateConv.csv", index=False)
    conversions = update_conversions_list(Update_Conv, conversions)
    conversions.to_csv("data/cleaning/Conversions_Added.csv", index=False)
    Std_Unit = pd.read_csv("data/external/standard_conversions.csv")
    liquid_unit, solid_unit = sort_liquid_and_solid_unit(Std_Unit)
    items_Nonstd = items_with_nonstd_units(ingredients, liquid_unit, solid_unit, conversions)
    items_Nonstd.to_csv("data/cleaning/Items_Nonstd.csv", index=False)
    preps = cleanup_preps_units(preps, conversions, Std_Unit)
    preps.to_csv("data/cleaning/Preps_Unit_Cleaned.csv", index=False)
    preps_nonstd = preps_with_nonstd_unit(preps)
    preps_nonstd.to_csv("data/cleaning/Preps_NonstdUom.csv", index=False)
    items_assigned = pd.read_csv("data/mapping/Items_List_Assigned.csv")
    new_items = sort_new_items(items, items_assigned)
    if not new_items.empty:
        new_items.insert(1, "CategoryID", "")
        new_items.to_csv("data/mapping/new items/" + str(datetime.date(datetime.now())) + "_New_Items.csv",
                         index=False)

    step2_summary = pd.DataFrame([new_items.shape, preps_nonstd.shape, items_Nonstd.shape],
                                 columns=["Count", "Columns"],
                                 index=["New_Items", "Preps_Nonstd", "Items_Nonstd"])
    print(step2_summary)

    # Step 3: update info and mapping
    '''
    This process includes manual steps.
    Make sure to go through them in order. Incorrect order will raise an error. 
    1) Go to `data/mapping/new items/date_New_Items.csv`. The number of new items added onto the file should match 
       how many of them have been reported in step 2. 
    2) Assign category ID to the new items added. 
    3) Copy and paste the items from the above step onto `data/mapping/new items/New_Items_Added_no.
    3) Check `data/cleaning/Preps_NonstdUom.csv` to find out preps with non-standard units. 
       Manually convert their units into standard units (ml or g) and paste the info to 
       `data/cleaning/update/Preps_UpdateUom.csv`. Use online search to manually convert the units. 
    4) Do the same as above with the file `data/cleaning/Items_Nonstd.csv`. 
       Manually convert the units and paste to `data/cleaning/update/Conv_UpdateConv.csv`.
    '''
    print("\nStep 3: Update info and Mapping begins...")
    manual_factor = pd.read_csv("data/mapping/Manual_Adjust_Factors.csv")
    manual_prep = pd.read_csv("data/cleaning/update/Preps_UpdateUom.csv")
    preps = update_uom_for_preps(manual_prep, preps)
    preps.drop_duplicates(subset=["PrepId"], inplace=True)
    preps.to_csv("data/cleaning/Preps_List_Cleaned.csv", index=False)
    # Change the file below each time new items are added.
    new_items_added = pd.read_csv("data/mapping/new items added/New_Items_Added_20.csv")
    items_assigned_updated = import_list_of_new_items_with_emission_factors(items_assigned, new_items_added)
    items_assigned_updated.to_csv("data/mapping/Items_List_Assigned.csv", index=False)

    ghge_factors = pd.read_csv("data/external/ghge_factors.csv")
    nitro_factors = pd.read_csv("data/external/nitrogen_factors.csv")
    water_factors = pd.read_csv("data/external/water_factors.csv")
    print("\nStep 3: Here1.")

    # most recently added
    land_factors = pd.read_csv("data/external/land_factors.csv")
    print("\nhere2.")

    items_assigned_updated = pd.read_csv("data/mapping/Items_List_Assigned.csv")
    mapping = map_items_to_ghge_factors(items_assigned_updated, ghge_factors)
    print("\nhere3.")
    mapping = map_items_to_nitrogen_factors(mapping, nitro_factors)
    print("\nhere4.")
    mapping = map_items_to_water_factors(mapping, water_factors)

    # most recently added
    mapping = map_items_to_land_factors(mapping, land_factors)
    print("\nhere5.")
    # COMMENTED OUT THE LINE BELOW!!
    # mapping = manual_adjust_factors(manual_factor, mapping)

    mapping["CategoryID"] = mapping["CategoryID"].astype("int")
    mapping.to_csv("data/mapping/Mapping.csv", index=False)

    if mapping["CategoryID"].isnull().sum() == 0:
        print("Clear!", mapping["CategoryID"].isnull().sum(), "items have non-assigned CategoryID.")
    else:
        print("`data/mapping/Mappings.csv` has", mapping["CategoryID"].isnull().sum(), "unassigned CategoryID.")
        print("Please modify before proceeding.")
        exit()
    # print("\nhere6.")

    # Step 4: data analysis
    print("\nStep 4: Data Analysis begins...")
    spc_cov = list(filter(None, conversions['ConversionId'].tolist()))
    conversions = unit_conversion_for_preps(manual_prep, conversions)

    conversions.dropna(axis=0, how="all", inplace=True)
    preps = rearrange_preps(preps)

    for index, row in preps.iterrows():
        get_items_ghge_prep(index, row, ingredients, preps, mapping, spc_cov, conversions, liquid_unit, solid_unit,
                            Std_Unit)
    for index, row in preps.iterrows():
        link_preps(index, row, ingredients, preps, spc_cov, conversions, liquid_unit, solid_unit, Std_Unit)
    for index, row in preps.iterrows():
        get_preps_ghge_prep(index, row, ingredients, preps, spc_cov, conversions, liquid_unit, solid_unit, Std_Unit)

    products = rearrange_products(products)
    for index, row in products.iterrows():
        get_items_ghge(index, row, ingredients, products, mapping, conversions, liquid_unit, solid_unit, Std_Unit)
    for index, row in products.iterrows():
        get_preps_ghge(index, row, ingredients, products, preps, conversions, liquid_unit, solid_unit, Std_Unit)
    for index, row in products.iterrows():
        get_products_ghge(index, row, ingredients, products)

    for index, row in products.iterrows():
        filter_products(index, row, ingredients, preps_nonstd, products)

    products = products_cleanup(products)
    assert assertpoint == products.shape[0], "Step 4: Products shape do not match."
    # products.to_csv("data/final/Recipes Footprints2.csv", index=False)
    print("Clear! Moving on.")

    # Step 5: data labelling
    print("\nStep 5: Data Labelling begins...")
    final = products.copy()

    final["GHG Only Label"] = final["GHG Emission (g) / 100g"].apply(lambda x: create_ghg_label(x))
    final = create_results_all_factors(final)
    assert assertpoint == products.shape[0], "Step 5: Products shape do not match."
    final = create_category_true(final)
    final.to_csv(f"data/final/2022_2023_CFFS_Outcomes/Data_Labelled_{restaurant_name}.csv", index=False)
    final.to_excel(f"data/final/2022_2023_CFFS_Outcomes/Data_Labelled_{restaurant_name}.xlsx",
                   sheet_name="Labels", index=False)
    final2 = final.copy()
    final2 = add_menu_names(final, Gather_list)
    # final2 = create_category_true(final2)
    final2.to_csv(f"data/final/2022_2023_CFFS_Outcomes/Data_Labelled_{restaurant_name}_with_name.csv",
                  index=False)
    final2.to_csv(f"data/final/2022_2023_CFFS_Outcomes/Data_Labelled_{restaurant_name}_with_name.xlsx",
                  index=False)

    print(final2)
    counts = create_final_counts(final2)
    all_ghg_num = counts["GHG Label Counts"].sum()
    all_num = counts["Combined Label Counts"].sum()
    sum_row = pd.Series(data={"GHG Label Counts": all_ghg_num, "Combined Label Counts": all_num},
                        name="Sum")
    # counts = counts.append(sum_row, ignore_index=False)
    # counts.to_csv(f"data/final/2022_2023_CFFS_Outcomes/{restaurant_name}_Summary.csv", index=False)
    #
    # print(counts)
    counts_print = pd.concat([counts, sum_row], ignore_index=True)
    # counts_print = pd.concat([counts, sum_row], ignore_index=False)

    # Original below that was causing error was because using append instead of concat
    # counts_print = counts.append(sum_row, ignore_index=False)
    counts_print.to_csv(f"data/final/2022_2023_CFFS_Outcomes/{restaurant_name}_Summary.csv", index=False)

    print(counts_print)
    if (counts["GHG Label Counts"].sum() == counts["Combined Label Counts"].sum()) \
            & (counts["GHG Label Counts"].sum() == assertpoint):
        print("Clear! All products have been labelled successfully. \nProcess finished.")
    else:
        print("Error! Some products have not been assigned successfully. Please revise.")

    fig = create_visualizations(counts)
