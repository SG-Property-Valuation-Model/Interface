# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
import dash 
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

import listing
from dash.exceptions import PreventUpdate


### Declaring Stylesheets for Layout ##################################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.SANDSTONE]
app = dash.Dash(__name__, external_stylesheets = external_stylesheets, suppress_callback_exceptions=True)

### Input Component ###################################################################

property_type_dropdown = [
    dbc.DropdownMenuItem("Apartment", id="property-dropdown-apt"),
    dbc.DropdownMenuItem("Condo", id="property-dropdown-condo"),
    dbc.DropdownMenuItem("EC", id="property-dropdown-ec"),
]

form_section = html.Div([
    
    # First row of inputs
    dbc.Row([
        dbc.Col(
            dbc.FormGroup(
                dbc.InputGroup([dbc.InputGroupAddon(dbc.Button("Postal Code", 
                                                               style = {'padding-left': 30, 'padding-right': 30}), 
                                                    addon_type = "prepend", 
                                                    #style = {'font-size': 'large'}
                                                    ), 
                                dbc.Input(id = 'postal-input', style = {'font-size': 'large', 'text-align': 'center'})],
                                size="lg", 
                                style = {'width': '-webkit-fill-available'}), 
                #className="mr-3", #style = {'width': '50%'}
                ),
            width = 4
        ),
        
        dbc.Col(
            dbc.FormGroup(
                dbc.InputGroup([dbc.DropdownMenu(property_type_dropdown,
                                                 bs_size="lg",
                                                 label = "Property Type", 
                                                 addon_type = "prepend"), 
                                dbc.Input(id="property-type-dropdown-input", style = {'font-size': 'large', 'padding-left': 20})],
                                size="lg", 
                                style = {'width': '-webkit-fill-available'}), 
                #className="mr-3", #style = {'width': '50%'}
                ),
            width = 8
        ),
        
    ], style = {'padding': 50, 'padding-bottom': 20, 'padding-top': 0}),
    
    # Second row of inputs
    dbc.Row([
        dbc.Col(
            dbc.FormGroup(
                dbc.InputGroup([dbc.InputGroupAddon(dbc.Button("Floor Number", 
                                                               style = {'padding-left': 30, 'padding-right': 30}), 
                                                    addon_type = "prepend", 
                                                    #style = {'font-size': 'large'}
                                                    ), 
                                dbc.Input(id = 'floor-num-input', style = {'font-size': 'large', 'text-align': 'center'})],
                                size="lg", 
                                style = {'width': '-webkit-fill-available'}), 
                #className="mr-3", #style = {'width': '50%'}
                ),
            width = 3
        ), 
        dbc.Col(
            dbc.FormGroup(
                dbc.InputGroup([dbc.InputGroupAddon(dbc.Button("Floor Area", 
                                                               style = {'padding-left': 30, 'padding-right': 30}), 
                                                    addon_type = "prepend", 
                                                    #style = {'font-size': 'large'}
                                                    ), 
                                dbc.Input(id = 'floor-area-input', style = {'font-size': 'large', 'text-align': 'center'}),
                                dbc.InputGroupAddon("SQM", addon_type="append")], 
                                size="lg", 
                                style = {'width': '-webkit-fill-available'}), 
                #className="mr-3", #style = {'width': '50%'}
                ),
            width = 3
        ), 
        dbc.Col(
            dbc.FormGroup(
                dbc.InputGroup([dbc.InputGroupAddon(dbc.Button("Remaining Lease", 
                                                               style = {'padding-left': 30, 'padding-right': 30}), 
                                                    addon_type = "prepend", 
                                                    #style = {'font-size': 'large'}
                                                    ), 
                                dbc.Input(id = 'lease-input', style = {'font-size': 'large', 'text-align': 'center'}),
                                dbc.InputGroupAddon("Years", addon_type="append")], 
                                size="lg", 
                                style = {'width': '-webkit-fill-available'}), 
                #className="mr-3", #style = {'width': '50%'}
                ),
            width = 4
        ), 
        
        # Submit button for form
        dbc.Col(
            dbc.Button("Submit", id='submit-val',
                       color = 'primary',
                       style = {'padding-left': 30, 'padding-right': 30}
                      
           )    
        )
        
    ], style = {'padding': 50, 'padding-top': 0})

])

input_section = html.Div( 
    [
        html.H1('UrbanZoom', style = {'padding': 50, 'padding-bottom': 20, 'font-weight': 'bold', 'color': 'antiquewhite'}),
        form_section
    ], 
        
    style = {'background-image': 'url("/assets/background4.jpg")', 
             'background-position': 'center', 
             'background-repeat': 'no-repeat', 
             'background-size': 'cover'}
)

### Overview Component ###################################################################

overview = html.Div([
    html.H1(children="Enter your property's details!", id='building-name', style={'fontSize': 25}),
    html.Div(children="", id='predicted-price-psm', style={'fontSize': 20}),
    html.Div(children="", id='predicted-price', style={'fontSize': 20})
], style = {'padding': 50})

### Runnning App ###################################################################

app.layout = html.Div([
    input_section, 
    overview    
])

### Callbacks from the input component
@app.callback(dash.dependencies.Output("property-type-dropdown-input", "value"),
             [dash.dependencies.Input("property-dropdown-ec", "n_clicks"),
              dash.dependencies.Input("property-dropdown-condo", "n_clicks"),
              dash.dependencies.Input("property-dropdown-apt", "n_clicks")])

def property_input_dropdown(n1, n2, n_clear):
    ctx = dash.callback_context

    if not ctx.triggered:
        return ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "property-dropdown-ec":
        return "Executive Condominium"
    elif button_id == "property-dropdown-condo":
        return "Condominium"
    elif button_id == "property-dropdown-apt":
        return "Apartment"
    else:
        return ""

### Callbacks from the input component -- output predicted price for the listing
@app.callback(
    [dash.dependencies.Output("predicted-price-psm", 'children'),
    dash.dependencies.Output("predicted-price", 'children'),
    dash.dependencies.Output("building-name", 'children')],
    dash.dependencies.Input('submit-val', 'n_clicks'),
    [dash.dependencies.State("postal-input", "value"),
    dash.dependencies.State("property-type-dropdown-input", "value"),
    dash.dependencies.State("floor-num-input", "value"),
    dash.dependencies.State("floor-area-input", "value"),
    dash.dependencies.State("lease-input", "value")])

def display_predicted_price(n_clicks, postal_input, property_type, floor_num, floor_area, lease):
    if n_clicks is None or postal_input == '' or property_type == '' or floor_num == '' or floor_area == '' or lease == '':
        print("NOT CALLED BACK")
        raise PreventUpdate
    else:
        property = listing.Listing(postal_input, property_type, floor_num, floor_area, lease)
        # Read in dataframes
        sch = pd.read_csv('datasets/primary_sch_gdf.csv')
        area_df = pd.read_csv('datasets/area_centroid.csv')
        modelling = pd.read_csv('datasets/modelling_dataset.csv') # to be replaced by new modelling dataset
        cols = list(modelling.columns)
        cols.remove('Unit Price ($ PSM)')

        price_unit, price_psm = property.pred_price('modelling/', cols, area_df, sch)
        # Outputs to be displayed on dash
        price_psm_output = "Predicted price per sqm: ${:,.2f}".format(price_psm)
        price_output =  "Predicted price: ${:,.2f}".format(price_unit)
        building = property.get_building()
        building_output = "Building Name: " + building
    return [price_psm_output, price_output, building_output]

if __name__ == '__main__': 
    app.run_server(debug = False)
