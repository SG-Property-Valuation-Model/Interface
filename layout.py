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
from Sample import Sample
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
                                                 style = {'padding-left': 30},
                                                 addon_type = "prepend"), 
                                dbc.Input(id="property-type-dropdown-input", style = {'font-size': 'large', 'padding-left': 20})],
                                size="lg", 
                                style = {'width': '-webkit-fill-available'}), 
                #className="mr-3", #style = {'width': '50%'}
                ),
            width = 5
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
                       color = 'secondary',
                       style = {'padding-left': 30, 'padding-right': 30, 'color': 'orange'}
                      
           )    
        )
        
    ], style = {'padding': 50, 'padding-top': 0})

])

input_section = html.Div( 
    [
        html.H1('UrbanZoom', style = {'padding': 50, 'padding-bottom': 20, 'font-weight': 'bold', 'color': 'antiquewhite', 'font-size': 'xx-large'}),
        form_section
    ], 
        
    style = {'background-image': 'url("/assets/background4.jpg")', 
             'background-position': 'center', 
             'background-repeat': 'no-repeat', 
             'background-size': 'cover'}
)

### Overview Component ###################################################################

def derived_feature(logo, title, description): 
    feature = dbc.Col([
        dbc.Row([
            dbc.Col(html.Img(src=app.get_asset_url(logo), style = {'width': 50}), width = 2), 
            dbc.Col([
                html.Div(title, style = {'font-size': 'large'}),
                html.Div(description, style = {'font-size': 'small', 'color': 'grey'})
            ], style = {'padding-top': 5, 'padding-left': 30})
        ], style = {'padding': 10}), 
    ], width = 4)

    return feature
    

listing_feature = [
    dbc.CardHeader(children="", id='predicted-price', style = {'font-size': 'x-large', 'padding': 10, 'padding-left': 20}), 
    dbc.CardBody([
        dbc.Row([
            derived_feature('train.png', 'Clementi . Kent Ridge', "Train stations within 1km"),
            derived_feature('train.png', 'Clementi . Kent Ridge', "Train stations within 1km"),
        ]), 
        dbc.Row([
            derived_feature('train.png', 'Clementi . Kent Ridge', "Train stations within 1km"),
            derived_feature('train.png', 'Clementi . Kent Ridge', "Train stations within 1km"),
            derived_feature('train.png', 'Clementi . Kent Ridge', "Train stations within 1km")
        ])
    ], style = {'paddding': 20})    
]

overview = html.Div([
    html.Ol(
        [
            html.Li(html.A("overview", href = "#overview", style = {'padding-right': 10}), className = 'breadcrumb-item'),
            html.Li(html.A("historic transactions", href = "#past_transactions", style = {'color': 'darkgrey', 'padding-right': 10, 'padding-left': 10}), className = 'breadcrumb-item active'), 
            html.Li(html.A("current resale climate", href = "#resale_climate", style = {'color': 'darkgrey', 'padding-right': 10, 'padding-left': 10}), className = 'breadcrumb-item active')
        ], 
        className = 'breadcrumb', 
        style = {'height': 40, 'font-size': 'large', 'background-color': 'white', 'border-color': 'white', 'padding-left': 0}
    ),
    html.H1(children="Enter your property's details!", id='building-name', style = {'font-wieght': 'bold', 'font-size': 'xxx-large'}), 
    html.Div(children="", id='predicted-price-psm', style={'fontSize': 20}),
    html.Ol(
        [
            html.Li("Anderson Cross", style = {'padding-right': 5}, className = 'breadcrumb-item active'),
            html.Li("Level 16", style = {'padding-left': 5}, className = 'breadcrumb-item active'), 
            
        ], 
        className = 'breadcrumb', 
        style = {'height': 25, 'font-size': 'medium', 'background-color': 'white', 'border-color': 'white', 'padding': 0}
    ),
    html.Div(dbc.Card(listing_feature, color = 'light'))
    
], style = {'padding': 50}, id = 'overview')

### Historic Transactions Component ################################################

historic_transactions = html.Div(
    [   
        html.H1('Past Transactions', style = {'font-size': 'xxx-large'}), 
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                #html.Div('Planning Area', style = {'font-size': 'large', 'color': 'darkgrey'}),
                                html.Div('Choa Chu Kang', style = {'font-size': 'xx-large', 'height': 40}), 
                                html.Div('Planning Area', style = {'font-size': 'large', 'color': 'darkgrey'})
                            ], style = {'padding-bottom': 10, 'padding-left': 20, 'padding-top': 7}
                        ), 
                        
                        dbc.CardBody(
                            [   
                                dbc.Row([
                                    dbc.Col('$4079', style = {'font-size': 'xx-large', 'text-align': 'center', 'margin': 'auto', 'color': '#93C54B'}, width = 5),
                                    dbc.Col([
                                        html.Div('Average Unit Price', style = {'font-size': 'large', 'height': 25}), 
                                        html.Div('(per SQM)', style = {'font-size': 'medium', 'color': 'darkgrey'})
                                    ], style = {'font-size': 'large'})
                                ]),
                                
                                html.Br(),
                                html.Hr(style = {'padding': 10}),
                                
                                dbc.Row([
                                    dbc.Col('125', style = {'font-size': 'xx-large', 'text-align': 'center', 'margin': 'auto', 'color': '#93C54B'}, width = 5),
                                    dbc.Col([
                                        html.Div('Average Floor Area', style = {'font-size': 'large', 'height': 25}), 
                                        html.Div('(SQM)', style = {'font-size': 'medium', 'color': 'darkgrey'})
                                    ], style = {'font-size': 'large'})
                                ]), 
                                
                                html.Br(),
                                html.Hr(style = {'padding': 10}),
                                
                                dbc.Row([
                                    dbc.Col('500', style = {'font-size': 'xx-large', 'text-align': 'center', 'margin': 'auto', 'color': '#93C54B'}, width = 5),
                                    dbc.Col([
                                        html.Div('No. of Past Transactions', style = {'font-size': 'large', 'height': 25, 'line-height': '1.35'}), 
                                        #html.Div('(per SQM)', style = {'font-size': 'medium', 'color': 'darkgrey'})
                                    ], style = {'font-size': 'large'})
                                ])
                                
                            ], style = {'padding': 20}
                        )
                    ], 
                    
                    style = {'height': 'fit-content'}, 
                    color = 'light', 
                ),
                
            ], width = 4, style = {'padding-right': 0}),
            
            dbc.Col([
                dbc.Card([], color = 'secondary', style = {'height': 380})    
            ], width = 8, style = {'padding-left': 0})
            
        ])
    
    ],
    style = {'padding': 50, 'padding-top': 20}, 
    id = 'past_transactions'
)

### Resale Climate Component #######################################################

resale_climate = html.Div(
    [
         html.H1('Resale Climate', style = {'font-size': 'xxx-large'}), 
         html.Br(),
    ], 
    style = {'padding': 50, 'padding-top': 20}, 
    id = 'resale_climate'
)



### Runnning App ###################################################################

app.layout = html.Div([
    input_section, 
    overview, 
    historic_transactions, 
    resale_climate
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
        train = pd.read_csv('datasets/train_gdf.csv')
        area_df = pd.read_csv('datasets/area_centroid.csv')
        modelling = pd.read_csv('datasets/modelling_dataset.csv')
        police_centre = pd.read_csv('datasets/police_centre_gdf.csv')
        avg_cases_by_npc = pd.read_csv('datasets/average_cases_by_npc.csv')
        cols = list(modelling.columns)
        cols.remove('Unit Price ($ PSM)')

        price_unit, price_psm = property.pred_price('modelling/', cols, area_df, sch, train, police_centre, avg_cases_by_npc)
        # Outputs to be displayed on dash
        price_psm_output = "Predicted price per sqm: ${:,.2f}".format(price_psm)
        price_output =  "Predicted price: ${:,.2f}".format(price_unit)
        building = property.get_building()
        building_output = "Building Name: " + building
    return [price_psm_output, price_output, building_output]

if __name__ == '__main__': 
    app.run_server(debug = False)
