# Importing required modules
import components as components  # custom module
import pandas as pd
import numpy as np
import dash
from dash import Dash, html, dcc, dash_table, ctx
import dash_bootstrap_components as dbc
from dash import callback_context
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import plotly
import os
import plotly.express as px
import plotly.graph_objects as go
import base64

# Reading data from CSV files and merging them
OK = pd.read_csv("C:/Users/smvan/CFFS-S23/CFFS-22-23/data/final/2022_2023_CFFS_Outcomes/Data_Labelled_OK22"
                 "-23_with_name.csv")
OK = OK.dropna(subset=["Category"])
OK["Restaurant"] = "Open Kitchen"

Gather = pd.read_csv("C:/Users/smvan/CFFS-S23/CFFS-22-23/data/final/2022_2023_CFFS_Outcomes/Data_Labelled_Gather22"
                     "-23_with_name.csv")
Gather = Gather.dropna(subset=["Category"])
Gather["Restaurant"] = "Gather"

Feast = pd.read_csv("C:/Users/smvan/CFFS-S23/CFFS-22-23/data/final/2022_2023_CFFS_Outcomes/Data_Labelled_Feast22"
                    "-23_with_name.csv")
Feast = Feast.dropna(subset=["Category"])
Feast["Restaurant"] = "Feast"

df = pd.concat([OK, Gather], axis=0)  # Merging the dataframes
df = df.reset_index().drop(["index"], axis=1)
df = pd.concat([df, Feast], axis=0)

# Renaming columns of the merged dataframe
df = df.rename(columns={"GHG Emission (g) / 100g": "GHG Emission",
                        "N lost (g) / 100g": "Nitrogen Lost",
                        "Freshwater Withdrawals (L) / 100g": "Freshwater Withdrawals",
                        "Combined Label": "Label"})

# Saving the merged dataframe to a new CSV file
df.to_csv("C:/Users/smvan/CFFS-S23/CFFS-22-23/data/final/2022_2023_CFFS_Outcomes/UBCFS_summary.csv")

# Printing some information about the merged dataframe
print(df)
print(len(df))

# Setting up the Dash app and defining the layout
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc_css])  # Creating a Dash app instance
image_path = "../image/ubc-logo.png"  # Path to the UBC logo image

server = app.server

# Encoding the UBC logo image using base64 encoding for use in the app
encoded_image = base64.b64encode(open(image_path, "rb").read())

# Set up the layout for the web application
app.layout = html.Div([

    # Create a row for the application content
    dbc.Row([

        # First column of the row
        dbc.Col([

            # Create a div containing the logo, title, and dropdown menus
            html.Div([

                # First row under the first column containing the logo
                dbc.Row([
                    dbc.Col(html.Img(
                        # Use the encoded image data as the image source
                        src='data:image/png;base64,{}'.format(encoded_image.decode()),
                        style={"margin-top": "10px"}
                    ))
                ],
                    # Apply styles to the row
                    style={"textAlign": "center", "margin-top": "18px", "margin-bottom": "10px"}),

                # Second row under the first column containing the title
                dbc.Row([
                    dbc.Col(html.H1(
                        "Residance Hall Food Emission Labels",
                        style={"textAlign": "center", "margin-bottom": "15px", "margin-top": "20px",
                               "color": "white", "fontSize": 16}
                    ))
                ]),

                # Third row under the first column containing the restaurant dropdown menu
                dbc.Row([
                    html.Label("Select Restaurant:", style={"color": "white"}),
                    dcc.Dropdown(
                        id="restaurant_dropdown",
                        options=[{"label": r, "value": r} for r in df["Restaurant"].unique().tolist()],
                        value="Restaurant",
                        multi=False,
                        style={"margin-bottom": "10px"}
                    )
                ]),

                # Fourth row under the first column containing the category dropdown menu
                dbc.Row([
                    html.Label("Select Category:", style={"color": "white"}),
                    dcc.Dropdown(
                        id="category_dropdown",
                        options=[],
                        value="Category",
                        multi=False,
                        style={"margin-bottom": "10px"}
                    )
                ]),

                # Fifth row under the first column containing the item dropdown menu
                dbc.Row([
                    html.Label("Select Menu Item:", style={"color": "white"}),
                    dcc.Dropdown(
                        id="item_dropdown",
                        options=[],
                        value="Displayed Name",
                        multi=False,
                        style={"margin-bottom": "10px"}
                    )
                ]),
            ]),

            # Set the width of the first column to 3 and set its background color
        ], width=3, style={'background-color': '#002145'}),

        # Second column of the row
        dbc.Col([

            # Create a div containing a data table
            html.Div([
                dbc.Row([
                    dash_table.DataTable(
                        # Set the table to have horizontal scrolling
                        style_table={'overflowX': 'auto'},
                        id="menu_item_table",
                        # Set the columns of the table
                        columns=[{"name": i, "id": i, "deletable": True, "selectable": True, "type": "numeric"}
                                 for i in df.loc[:, ["ProdId", "Description", "GHG Emission",
                                                     "Nitrogen Lost", "Freshwater Withdrawals", "Label"]]],
                        # Set the data of the table
                        data=df.to_dict("records"),
                        # Set the initial state of the table to have no selected columns or rows
                        selected_columns=[],
                        selected_rows=[],
                        # Set the filter and page actions to use native filtering and paging
                        filter_action="native",
                        page_action="native",
                        # Set the table to have a list view style
                        style_as_list_view=True,
                        # Allow the table to be edited
                        editable=True,
                        # Sets the type of sorting to native.
                        sort_action="native",
                        # style_header defines the style for the table headers.
                        style_header={"backgroundColor": "rgb(12, 35, 68)",
                                      "fontweight": "bold", "color": "white",
                                      "font_size": "13px"},
                        # style_cell defines the style for the table cells.
                        style_cell={"font_family": "arial",
                                    "font_size": "12px",
                                    "text_align": "left"},
                        # style_data defines the style for the table data.
                        style_data={'backgroundColor': 'transparent'},
                        # sort_mode sets the type of sorting mode to single.
                        sort_mode="single")], style={"margin-top": "15px"}),

                # Display two Markdown components containing information about the emissions data.
                dbc.Row([
                    # The first Markdown component contains two bullet points explaining the units of measurement and
                    # basis of the emissions data.
                    dcc.Markdown(children="""
                    - All emission factors are calculated on basis of **100g** of the selected menu item.
                    - Unit of measurement: GHG Emission (g), Nitrogen lost (g), Freshwater Withdrawals (L).
                    """, style={"font_size": "15px"})
                ]),

                # The second Markdown component will be used to display additional information about the selected menu
                # items.
                dbc.Row([
                    dcc.Markdown(id="markdown_results")
                ]),

            ]),

            dbc.Row([
                # First column has a dbc.Card element containing a dcc.Input component
                # with an id of element_to_hide
                dbc.Col([
                    dbc.Card([
                        dcc.Input(id="element_to_hide"),
                        dbc.CardBody([html.H4("Test")], className="text-center"),
                    ])
                ], width=3),
                # Second column has dbc.Card element containing a dcc.Input component
                # component with an id of element_to_hide2
                dbc.Col([
                    dbc.Card([
                        dcc.Input(id="element_to_hide2"),
                        html.Img(id="label_figure")
                    ])
                ], width=9)
            ], style={"margin-top": "10px", "margin-bottom": "10px", "width": "100%",
                      "margin-left": "10px", "margin-right": "10px", "display": "none"}),

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        html.H2("Visualizations", style={"fontSize": 18, "textAlign": "center"}),
                        dbc.ButtonGroup([
                            dbc.Button("GHG Emissions", id="GHG_button", size="sm",
                                       style={"display": "inline-block", "verticalAlign": "middle",
                                              "background-color": "rgb(12, 35, 68)", "color": "white", 'width': '10em'},
                                       className="me-md-2"),
                            dbc.Button("Nitrogren Emissions", id="nitrogen_button", size="sm",
                                       style={"display": "inline-block", "verticalAlign": "middle",
                                              "background-color": "rgb(12, 35, 68)", "color": "white", 'width': '10em'},
                                       className="me-md-2"),
                            dbc.Button("Freshwater Withdrawals", id="freshwater_button", size="sm",
                                       style={"display": "inline-block", "verticalAlign": "middle",
                                              "background-color": "rgb(12, 35, 68)", "color": "white", 'width': '10em'},
                                       className="me-md-2")
                        ], className="border-0 bg-transparent"),

                    ], style={"border": "0px"}))
            ], style={"margin-top": "18px", "margin-bottom": "3px", "width": "100%",
                      "margin-left": "10px", "margin-right": "10px"}),

            html.Div(id="graph_content")

        ], width=9, style={'background-color': '#FFFFFF'}, className="dbc dbc-row-selectable")

    ], style={"height": "100vh"})

], style={"width": "100vw"})


# triggers the function when the restaurant_dropdown input value is changed
# output of the callback is the options of the category_dropdown component
@app.callback(
    Output("category_dropdown", "options"),
    [Input("restaurant_dropdown", "value")])
def get_category_per_restaurants(restaurant_dropdown):
    # df_categorized filers the DataFrame, df based on selected restaurant_dropdown value
    df_categorized = df[df["Restaurant"] == restaurant_dropdown]
    # returned value is a list comprehension that generates the option for the
    # category_dropdown dropdown component.
    return [{"label": c, "value": c} for c in df_categorized["Category"].unique()]


# callback is triggered with either category_dropdown or restaurant_dropdown input changes
@app.callback(
    Output("item_dropdown", "options"),
    [Input("category_dropdown", "value")],
    [Input("restaurant_dropdown", "value")])
def get_category_per_restaurants(category_dropdown, restaurant_dropdown):
    df_categorized = df[df["Restaurant"] == restaurant_dropdown]
    df_items = df_categorized[df_categorized["Category"] == category_dropdown]
    return [{"label": n, "value": n} for n in df_items["Displayed Name"].unique()]


# callback is triggered with either category_dropdown or restaurant_dropdown input changes
# the selected values of the dropdown menus are used to filter the data displayed in a table
@app.callback(
    Output("menu_item_table", "data"),
    [Input("restaurant_dropdown", "value")],
    [Input("category_dropdown", "value")],
    [Input("item_dropdown", "value")])
def get_selected_menu_item(restaurant_dropdown, category_dropdown, item_dropdown):
    # checks if restaurant_dropdown input is None, if it is then it returns all the data in the table
    if restaurant_dropdown is None:
        data = df.to_dict("records")
        return data
    # WHAT IS THE POINT OF THE IF STATEMENT BELOW SINCE WE ARE ALREADY CHECKING IF IS NONE RESTAURANT
    if (restaurant_dropdown is None) & (category_dropdown is None) & (item_dropdown is None):
        data = df.to_dict("records")
    if restaurant_dropdown is not None:
        df_categorized = df[df["Restaurant"] == restaurant_dropdown]
        data = df_categorized.to_dict("records")
    if (restaurant_dropdown is not None) & (category_dropdown is not None):
        df_categorized = df[df["Restaurant"] == restaurant_dropdown]
        df_items = df_categorized[df_categorized["Category"] == category_dropdown]
        data = df_items.to_dict("records")
    # if the inputs are not None, it filters the data by the selected values of the dropdown menus
    if (restaurant_dropdown is not None) & (category_dropdown is not None) & (item_dropdown is not None):
        df_categorized = df[df["Restaurant"] == restaurant_dropdown]
        df_items = df_categorized[df_categorized["Category"] == category_dropdown]
        df_selected = df_items[df_items["Displayed Name"] == item_dropdown]
        data = df_selected.to_dict("records")
    # If all three dropdown menus are selected, it filters the data to show only selected menu item
    return data


@app.callback(
    Output("markdown_results", "children"),
    [Input("restaurant_dropdown", "value")],
    [Input("category_dropdown", "value")],
    [Input("item_dropdown", "value")])
def get_label_displayed(restaurant_dropdown, category_dropdown, item_dropdown):
    df["Label"] = df["Label"].str.upper()
    # If any of the dropdowns are empty, return an empty string
    if (item_dropdown is None) or (restaurant_dropdown is None) or (category_dropdown is None):
        return ""
    if category_dropdown is None:
        return ""
    else:
        # Filter the dataframe to find the label of the selected item in the dropdowns
        df_label = df.loc[(df["Restaurant"] == restaurant_dropdown) & (df["Category"] == category_dropdown) & (
                df["Displayed Name"] == item_dropdown), "Label"].values[0]
        # df_label = df[(df["Restaurant"] == restaurant_dropdown) & (df["Category"] == category_dropdown) & (
        #         df["Displayed Name"] == item_dropdown)].Label.item()
        print(df_label)
        # return the label as a markdown string
        return f"**Selected item is labelled as {df_label}.**"


@app.callback(
    Output("markdown_results", "style"),
    [Input("markdown_results", "children")])
def get_label_colored(markdown_results):
    # Copy the markdown_results
    output = markdown_results
    print(output)
    # Check if the output string contains "YELLOW", and if it does, set the color to orange
    if "YELLOW" in output:
        color = {"color": "orange", "font_size": "15px"}
        return color
    # Check if the output string contains "RED", and if it does, set the color to red
    if "RED" in output:
        color = {"color": "red", "font_size": "15px"}
        return color
    # Check if the output string contains "GREEN", and if it does, set the color to green
    if "GREEN" in output:
        color = {"color": "green", "font_size": "15px"}
        return color
    # Else, set the color to grey
    else:
        color = {"color": "grey"}


@app.callback(
    # this callback function takes 3 inputs, which represent the numbe of times each of the
    # buttons is clicked. The output is graph_content which will be a container for the figure
    Output("graph_content", "children"),
    [Input("GHG_button", "n_clicks")],
    [Input("nitrogen_button", "n_clicks")],
    [Input("freshwater_button", "n_clicks")])
#     [State("restaurant_dropdown", "value")],
#     [State("category_dropdown", "value")],
#     [State("item_dropdown", "value")])
def display_histogram(GHG_button, nitrogen_button, freshwater_button):
    OK = df.loc[df["Restaurant"] == "Open Kitchen"]
    Gather = df.loc[df["Restaurant"] == "Gather"]
    Feast = df.loc[df["Restaurant"] == "Feast"]
    all_colors = {"Open Kitchen": "#4E68B2",
                  "Gather": "#E85B66",
                  "Feast": "#82C48C"}

    # below are 2 helper functions for the callback function.
    # all_restaurants generates a histogram and a boxplot figure that compares the input feature
    # across all 3 restaurant, while specific_restaurant generates the same figures for only one restaurant
    # there are 3 dataframes, "OK", "Gather" and "Feast" which are subsets which are subsets of the original dataframe
    # each containing data from a different restaurant.
    def all_restaurants(feature):
        # make_subplots creates a 1x2 subplot layout with titles, "Histogram" and "Boxplot", shared y-axis and no
        # legend
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Histogram", "Boxplot"), shared_yaxes=False)
        fig.add_trace(go.Histogram(x=OK[feature], nbinsx=20, opacity=0.8, name="Open Kitchen",
                                   marker_color=all_colors["Open Kitchen"]), row=1, col=1)
        fig.add_trace(
            go.Histogram(x=Gather[feature], nbinsx=20, opacity=0.8, name="Gather", marker_color=all_colors["Gather"]),
            row=1, col=1)
        fig.add_trace(
            go.Histogram(x=Feast[feature], nbinsx=20, opacity=0.8, name="Feast", marker_color=all_colors["Feast"]),
            row=1, col=1)
        fig.add_trace(go.Box(y=OK[feature], name="Open Kitchen", marker_color=all_colors["Open Kitchen"]), row=1, col=2)
        fig.add_trace(go.Box(y=Gather[feature], name="Gather", marker_color=all_colors["Gather"]), row=1, col=2)
        fig.add_trace(go.Box(y=Feast[feature], name="Feast", marker_color=all_colors["Feast"]), row=1, col=2)

        # customize layout of the figure below
        fig.update_xaxes(row=1, col=2, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_xaxes(row=1, col=1, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_yaxes(row=1, col=2, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_yaxes(row=1, col=1, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_layout(plot_bgcolor="white", showlegend=True, legend_title="Restaurant",
                          title=feature + " Comparisons Across Restaurants", title_x=0.5)

        names = set()
        fig.for_each_trace(
            lambda trace:
            trace.update(showlegend=False)
            if (trace.name in names) else names.add(trace.name))
        # function returns a figure (fig) that will be displayed in the graph_content container whenever any of the
        # three input buttons are clicked.
        return fig

    def specific_restaurant(df, feature):
        # creates a plot consisting of a histogram and boxplot for a specified feature column in a pandas DataFrame.
        # The function returns a plotly figure object.

        # make_subplots() function creates a subplot with two columns and one row. The subplot_titles argument sets
        # the titles for each subplot.
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Histogram", "Boxplot"), shared_yaxes=False)
        fig.add_trace(go.Histogram(x=df[feature], nbinsx=20, opacity=0.8), row=1, col=1)
        fig.add_trace(go.Box(y=df[feature]), row=1, col=2)
        # set axis labels, line and grid properties and line-width for both subplots
        fig.update_xaxes(title_text=feature, row=1, col=2, showline=True, linecolor="#002145", showgrid=True,
                         linewidth=1.2)
        fig.update_xaxes(title_text=feature, row=1, col=1, showline=True, linecolor="#002145", showgrid=True,
                         linewidth=1.2)
        fig.update_yaxes(row=1, col=2, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_yaxes(row=1, col=1, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_layout(plot_bgcolor="white", showlegend=False)
        return fig

    ctx = dash.callback_context
    button_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    # code checks which button was clicked using dash.callback_context and the triggered property
    if button_clicked == "GHG_button":
        fig = all_restaurants("GHG Emission")
        return dcc.Graph(id="GHG_graph", figure=fig)

    if button_clicked == "nitrogen_button":
        fig = all_restaurants("Nitrogen Lost")
        return dcc.Graph(id="nitrogen_graph", figure=fig)

    if button_clicked == "freshwater_button":
        fig = all_restaurants("Freshwater Withdrawals")
        return dcc.Graph(id="freshwater_graph", figure=fig)

    # if __name__ == "__main__": to run the Dash app in debug mode when the script is executed directly.
    # Not executed if the script is imported as a module into another script


if __name__ == "__main__":
    app.run_server(debug=True)
