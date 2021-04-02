# -*- coding: utf-8 -*-
"""
Contains frontend layout of interface

"""
import pandas as pd
import numpy as np
import dash 
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
from dash.exceptions import PreventUpdate

# Importing backend classes
from Sample import Sample
from listing import Listing

### Declaring Stylesheets for Layout ##################################
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.SANDSTONE]
app = dash.Dash(__name__, external_stylesheets = external_stylesheets, suppress_callback_exceptions=True)


### Parsing Data Required ##############################################
sch = pd.read_csv('datasets/primary_sch_gdf.csv')
train = pd.read_csv('datasets/train_gdf.csv')
area_df = pd.read_csv('datasets/area_centroid.csv')
modelling = pd.read_csv('datasets/modelling_dataset.csv')
police_centre = pd.read_csv('datasets/police_centre_gdf.csv')
avg_cases = pd.read_csv('datasets/average_cases_by_npc.csv')
prelim_ds = pd.read_csv('datasets/preliminary_dataset.csv')
postal_code_area = pd.read_csv('datasets/historical_postal_code_area.csv')
cols = list(modelling.columns)
prelim_ds['Sale Date'] = pd.to_datetime(prelim_ds['Sale Date'], format = '%Y-%m-%d')

### Global Objects #####################################################
global curr_listing
global curr_sample
global full_sample
default_params = {'radius': [0,0], 
                  'time': [0,0], 
                  'property': [1,1,1]}

full_sample = Sample(default_params, prelim_ds)

### Input Component ###################################################################

property_type_dropdown = [
    dbc.DropdownMenuItem("Apartment", id="property-dropdown-apt"),
    dbc.DropdownMenuItem("Condo", id="property-dropdown-condo"),
    dbc.DropdownMenuItem("EC", id="property-dropdown-ec"),
]

radius_dropdown = [
    dbc.DropdownMenuItem("Within 1km", id="radius-dropdown-1"),
    dbc.DropdownMenuItem("Within 2km", id="radius-dropdown-2"),
]

time_dropdown = [
    dbc.DropdownMenuItem("Past 5 Years", id="time-dropdown-5"),
    dbc.DropdownMenuItem("Past 10 Years", id="time-dropdown-10"),
]

form_section = html.Div([
    
    # First row of inputs
    dbc.Row([
        dbc.Col(
            dbc.FormGroup(
                dbc.InputGroup([dbc.InputGroupAddon(dbc.Button("Postal Code", color = 'dark',
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
                                                 color = 'dark',
                                                 bs_size="lg",
                                                 label = "Property Type", 
                                                 #style = {'padding-left': 30},
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
                dbc.InputGroup([dbc.InputGroupAddon(dbc.Button("Floor Number", color = 'dark',
                                                               style = {'padding-left': 30, 'padding-right': 30}), 
                                                    addon_type = "prepend", 
                                                    #style = {'font-size': 'large'}
                                                    ), 
                                dbc.Input(id = 'floor-num-input', style = {'font-size': 'large', 'text-align': 'center'})],
                                size="lg", 
                                style = {'width': '-webkit-fill-available'}), 
                #className="mr-3", #style = {'width': '50%'}
                ),
            width = 4
        ), 
        dbc.Col(
            dbc.FormGroup(
                dbc.InputGroup([dbc.InputGroupAddon(dbc.Button("Floor Area", color = 'dark',
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
            width = 4
        ), 
       dbc.Col(
            dbc.FormGroup(
                dbc.InputGroup([dbc.InputGroupAddon(dbc.Button("Remaining Lease", color = 'dark',
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
        
    ], style = {'padding': 50, 'padding-bottom': 20, 'padding-top': 0}), 
    
    dbc.Row([
        dbc.Col(
            dbc.FormGroup(
                dbc.InputGroup([dbc.DropdownMenu(radius_dropdown,
                                                 bs_size="lg",
                                                 label = "Search Radius", 
                                                 color = 'dark',
                                                 style = {'color': '#93C54B'},
                                                 addon_type = "prepend"), 
                                dbc.Input(id="radius-dropdown-input", style = {'font-size': 'large', 'padding-left': 20, 'textAlign': 'center'})],
                                size="lg", 
                                style = {'width': '-webkit-fill-available'}), 
                #className="mr-3", #style = {'width': '50%'}
                ),
            width = 4
        ),
        
        dbc.Col(
            dbc.FormGroup(
                dbc.InputGroup([dbc.DropdownMenu(time_dropdown,
                                                 bs_size="lg",
                                                 label = "Time Filter", 
                                                 color = 'dark',
                                                 #style = {'color': '#93C54B'},
                                                 addon_type = "prepend"), 
                                dbc.Input(id="time-dropdown-input", style = {'font-size': 'large', 'padding-left': 20, 'textAlign': 'center'})],
                                size="lg", 
                                style = {'width': '-webkit-fill-available'}), 
                #className="mr-3", #style = {'width': '50%'}
                ),
            width = 5
        ), 
        
    ], style = {'padding': 50, 'padding-bottom': 20, 'padding-top': 0}), 
    
    dbc.Row([

        dbc.Col([
            dbc.InputGroup([dbc.InputGroupAddon(dbc.Button('Apartment', 
                                                           style = {'padding-left': 30, 'padding-right': 30, 'color': '#93C54B' },
                                                           className = 'btn-dark'),
                                                addon_type = "prepend"), 
                            dbc.InputGroupAddon(dbc.RadioButton(id = 'apt-selected'), 
                                                addon_type = 'append')],
                            size="lg", 
                            #style = {'width': '-webkit-fill-available'}
            ), 
        ], width="auto"),
        
        dbc.Col([
            dbc.InputGroup([dbc.InputGroupAddon(dbc.Button('Condominium', 
                                                           style = {'padding-left': 30, 'padding-right': 30, 'color': '#93C54B'},
                                                           className = 'btn-dark'),
                                                addon_type = "prepend"), 
                            dbc.InputGroupAddon(dbc.RadioButton(id = 'condo-selected'), 
                                                addon_type = 'append')],
                            size="lg", 
                            style = {'width': '-webkit-fill-available'}
            ), 
        ], width="auto"), 
        
        dbc.Col([
            dbc.InputGroup([dbc.InputGroupAddon(dbc.Button('Executive Condominium', 
                                                           style = {'padding-left': 30, 'padding-right': 30, 'color': '#93C54B'},
                                                           className = 'btn-dark'),
                                                addon_type = "prepend"), 
                            dbc.InputGroupAddon(dbc.RadioButton(id = 'ec-selected'), 
                                                addon_type = 'append')],
                            size="lg", 
                            style = {'width': '-webkit-fill-available'}
            )
        ], width="auto"), 
        
        # Submit button for form
        dbc.Col(
            dbc.Button("Submit", id='submit-val', 
                       color = 'dark',
                       style = {'padding-left': 38, 'padding-right': 40, 'color': 'orange'}
                      
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

### Navigation bar #######################################################################
nav_bar = html.Div([
        
    html.Ol(
            [
                html.Li(html.A("overview", href = "#overview", style = {'padding-right': 10}), className = 'breadcrumb-item'),
                html.Li(html.A("historic transactions", href = "#past_transactions", style = {'color': 'darkgrey', 'padding-right': 10, 'padding-left': 10}), className = 'breadcrumb-item active'), 
                html.Li(html.A("current resale climate", href = "#resale_climate", style = {'color': 'darkgrey', 'padding-right': 10, 'padding-left': 10}), className = 'breadcrumb-item active')
            ], 
            className = 'breadcrumb', 
            style = {'height': 40, 'font-size': 'large', 'background-color': 'white', 'border-color': 'white', 'padding-left': 0}
        )
], style = {'padding': 50, 'padding-bottom': 0})

### Overview Component ###################################################################

def derived_feature(logo, title, description): 
    if ('NPC' not in str(title)):
        title = str(title).title()
    feature = dbc.Col([
        dbc.Row([
            dbc.Col(html.Img(src=app.get_asset_url(logo), style = {'width': 50}), width = 2), 
            dbc.Col([
                html.Div(title, style = {'font-size': 'large'}),
                html.Div(description, style = {'font-size': 'small', 'color': 'grey'})
            ], style = {'padding-top': 5, 'padding-left': 30})
        ], style = {'padding': 10}), 
    ], width = 7)

    return feature
    
def overview_section(listing, predicted_price,  predicted_price_psm):
    
    #predicted_price,  predicted_price_psm
    
    listing_feature = dbc.Row([
        
        # Card Header --> Displaying Predicted Price
        #dbc.CardHeader(children = predicted_price, 
        #               id='predicted-price', 
        #               style = {'font-size': 'large', 'padding': 10, 'padding-left': 20}
        #),
        
        # Card Boody --> Displaying derived features and Predicted PSM
        
        dbc.Col([
            
            dbc.Card([
                
                dbc.Row([
                    dbc.Col("${:,.2f}".format(predicted_price), 
                            style = {'font-size': 'xx-large', 'text-align': 'center', 'margin': 'auto', 'color': '#93C54B', 'padding-left': 0}, 
                            width = 6
                    ),
                    dbc.Col([
                        html.P(['Estimated Valuation of Property', 
                                #html.Span('(per SQM)', style = {'font-size': 'medium', 'color': 'darkgrey'})
                        ], style = {'font-size': 'large', 'padding-top': 5}), #'height': 25
                    ], style = {'font-size': 'large', 'padding-left': 0})
                ], style = {'height': '45%', 'padding': 20, 'align-items': 'center'}),
                
                #html.Br(),
                html.Hr(style = {'padding': 0}),
                
                dbc.Row([
                    dbc.Col("${:,.2f}".format(predicted_price_psm), 
                            style = {'font-size': 'xx-large', 'text-align': 'center', 'margin': 'auto', 'color': '#93C54B', 'padding-left': 0}, 
                            width = 6
                    ),
                    dbc.Col([
                        html.P(['Estimated Price Per Unit Area ', 
                                html.Span('(per SQM)', style = {'font-size': 'medium', 'color': 'darkgrey'})
                        ], style = {'font-size': 'large'}), #'height': 25 
                        #html.Div('(SQM)', style = {'font-size': 'medium', 'color': 'darkgrey'})
                    ], style = {'font-size': 'large', 'padding-left': 0})
                ], style = {'padding': 20, 'align-items': 'center'})
                
            ], style = {'height': 255, 'background-color': '#ebe9e6'}), 
        ], width = 5),
        
        dbc.Col([
            
            dbc.Card([
                
                #html.Div(children = predicted_price_psm, id='predicted-price-psm', style={'fontSize': 20, 'padding-left': 10}),
                
                # Train Stations Derived Features
                dbc.Row([
                    derived_feature('train.png', " . ".join(list(listing.train_stations(train))), "Train stations within 1km"),
                    dbc.Col([
                        html.Div(str(int(listing.train_dist(train))) + " metres", style = {'font-size': 'large'}),
                        html.Div("Distance to Nearest Train Station", style = {'font-size': 'small', 'color': 'grey'})
                    ], style = {'padding-top': 10})
                ], style = {'align-items': 'center'}), 
                
                # Schools Derived Features
                dbc.Row([
                    derived_feature('school.png', listing.sch_name(sch), "Nearest School"),
                    dbc.Col([
                        html.Div(str(int(listing.sch_dist(sch))) + " metres", style = {'font-size': 'large'}),
                        html.Div("Distance to Nearest School", style = {'font-size': 'small', 'color': 'grey'})
                    ], style = {'padding-top': 10})
                    #derived_feature('', str(int(listing.sch_dist(sch))) + " metres", "Distance to Nearest School")
                ], style = {'align-items': 'center'}), 
                
                # Schools Derived Features
                dbc.Row([
                    derived_feature('police-station.png', listing.get_police_centre(police_centre), "Nearest Police Station"),
                    dbc.Col([
                        html.Div(listing.get_centre_avg_cases(police_centre, avg_cases), style = {'font-size': 'large'}),
                        html.Div("Average Yearly Crime Rate", style = {'font-size': 'small', 'color': 'grey'})
                    ], style = {'padding-top': 10})
                    #derived_feature('', listing.get_centre_avg_cases(police_centre, avg_cases), "Average Yearly Crime Rate")
                ], style = {'align-items': 'center'})
            ], color = 'light', style = {'padding': 20})    
            
        ], width = 7)
    ], no_gutters = True)

    overview = html.Div([
        
        # Listing Details
        html.H1(listing.get_building().title() , id='building-name', style = {'font-wieght': 'bold', 'font-size': 'xxx-large'}), 
    
        html.Ol(
            [
                html.Li(listing.get_road_name(), style = {'padding-right': 5}, className = 'breadcrumb-item active'),
                html.Li('Level ' + str(listing.get_floor_num()), style = {'padding-left': 5}, className = 'breadcrumb-item active'), 
                
            ], 
            className = 'breadcrumb', 
            style = {'height': 25, 'font-size': 'medium', 'background-color': 'white', 'border-color': 'white', 'padding': 0}
        ),
        
        # Derived Features from Listing
        html.Div([listing_feature])
        
    ], style = {'padding': 50, 'padding-top': 15}, id = 'overview')
    
    return overview

### Historic Transactions Component ################################################ 

def transaction_features(sample): 
    transaction_features = [
        
        dbc.Row([
            dbc.Col('$' + str(sample.get_average_psm()), 
                    style = {'font-size': 'xx-large', 'text-align': 'center', 'margin': 'auto', 'color': '#93C54B', 'padding-left': 0}, 
                    width = 7
            ),
            dbc.Col([
                html.P(['Average Unit Price ', 
                        html.Span('(per SQM)', style = {'font-size': 'medium', 'color': 'darkgrey'})
                ], style = {'font-size': 'large', 'height': 25}), 
            ], style = {'font-size': 'large', 'padding-left': 0})
        ]),
        
        html.Br(),
        html.Hr(style = {'padding': 10}),
        
        dbc.Row([
            dbc.Col(sample.get_average_floor_area(), 
                    style = {'font-size': 'xx-large', 'text-align': 'center', 'margin': 'auto', 'color': '#93C54B', 'padding-left': 0}, 
                    width = 7
            ),
            dbc.Col([
                html.P(['Average Floor Area ', 
                        html.Span('(SQM)', style = {'font-size': 'medium', 'color': 'darkgrey'})
                ], style = {'font-size': 'large', 'height': 25}), 
                #html.Div('(SQM)', style = {'font-size': 'medium', 'color': 'darkgrey'})
            ], style = {'font-size': 'large', 'padding-left': 0})
        ]), 
        
        html.Br(),
        html.Hr(style = {'padding': 10}),
        
        dbc.Row([
            dbc.Col(sample.get_total_transactions(), 
                    style = {'font-size': 'xx-large', 'text-align': 'center', 'margin': 'auto', 'color': '#93C54B', 'padding-left': 0}, 
                    width = 6
            ),
            dbc.Col([
                html.Div('Number of Past Transactions', style = {'font-size': 'large', 'height': 25, 'line-height': '1.35'}), 
                #html.Div('(per SQM)', style = {'font-size': 'medium', 'color': 'darkgrey'})
            ], style = {'font-size': 'large', 'padding-left': 0})
        ]) 
    ]
    return transaction_features

historic_transactions = html.Div(
    [   
        html.H1('Past Transactions', style = {'font-size': 'xxx-large'}), 
        html.Br(),
        dbc.Row([
            # Details of Transactions
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                #html.Div('Planning Area', style = {'font-size': 'large', 'color': 'darkgrey'}),
                                html.Div(id = 'planning-area-val',  style = {'font-size': 'xx-large', 'height': 40}), 
                                html.Div('Planning Area', style = {'font-size': 'large', 'color': 'darkgrey'})
                            ], style = {'padding-bottom': 10, 'padding-left': 20, 'padding-top': 7}
                        ), 
                        
                        dbc.CardBody(id = 'transaction-features', style = {'padding': 20})
                    ], 
                    
                    style = {'height': 'fit-content'}, 
                    color = 'light', 
                ),
                
            ], width = 4, style = {'padding-right': 0}),
            
            # Map showing transactions
            dbc.Col([
                dbc.Card(id = 'map', style = {'height': 380}, color =  'active') #'color': '#ebe9e6'    
            ], width = 8, style = {'padding-left': 0})
            
        ]), 
        html.Div(id = 'transaction-table', style = {'padding-top': 50})
    
    ],
    style = {'padding': 50, 'padding-top': 15}, 
    id = 'past_transactions'
)

### Resale Climate Component #######################################################

resale_climate = html.Div(
    [
         html.H1('Resale Climate', style = {'font-size': 'xxx-large'}), 
         html.Div(id = 'psm-timeseries-plot', style = {'padding-left': 10})
    ], 
    style = {'padding': 50, 'padding-top': 20}, 
    id = 'resale_climate'
)



### Runnning App ###################################################################

app.layout = html.Div([
    input_section,
    dbc.Spinner(id = 'loading'),
    nav_bar,
    html.Div(id = 'overview-section'), 
    historic_transactions, 
    resale_climate
])

@app.callback(dash.dependencies.Output('loading', 'children'), 
              [dash.dependencies.Input('submit-val', 'n_clicks')])

def load_output(n):
    if n: 
        return " "
    else: 
        return" "

### Callbacks for property-type-dropdown within input_section
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

@app.callback(dash.dependencies.Output("radius-dropdown-input", "value"),
             [dash.dependencies.Input("radius-dropdown-1", "n_clicks"),
              dash.dependencies.Input("radius-dropdown-2", "n_clicks")])

def radius_input_dropdown(n1, n_clear):
    ctx = dash.callback_context

    if not ctx.triggered:
        return ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "radius-dropdown-1":
        return "Within 1km"
    elif button_id == "radius-dropdown-2":
        return "Within 2km"
    else:
        return ""
    
@app.callback(dash.dependencies.Output("time-dropdown-input", "value"),
             [dash.dependencies.Input("time-dropdown-5", "n_clicks"),
              dash.dependencies.Input("time-dropdown-10", "n_clicks")])

def time_input_dropdown(n1, n_clear):
    ctx = dash.callback_context

    if not ctx.triggered:
        return ""
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "time-dropdown-5":
        return "Past 5 Years"
    elif button_id == "time-dropdown-10":
        return "Past 10 Years"
    else:
        return ""

### Callbacks from the input component -- output predicted price for the listing
@app.callback(
    #Outputs of Callback
    [dash.dependencies.Output("overview-section", 'children'), 
     dash.dependencies.Output('planning-area-val', 'children'), 
     dash.dependencies.Output("transaction-features", 'children'), 
     dash.dependencies.Output("map", 'children'), 
     dash.dependencies.Output("transaction-table", 'children'), 
     dash.dependencies.Output('psm-timeseries-plot', 'children')],
    
    #Inputs of Callback
    [dash.dependencies.Input('submit-val', 'n_clicks'),
     dash.dependencies.Input('apt-selected', 'checked'), 
     dash.dependencies.Input('ec-selected', 'checked'), 
     dash.dependencies.Input('condo-selected', 'checked'),
     dash.dependencies.Input("time-dropdown-input", "value"), 
     dash.dependencies.Input("radius-dropdown-input", "value"),
     dash.dependencies.State("postal-input", "value"),
     dash.dependencies.State("property-type-dropdown-input", "value"),
     dash.dependencies.State("floor-num-input", "value"),
     dash.dependencies.State("floor-area-input", "value"),
     dash.dependencies.State("lease-input", "value")]
)

def display_predicted_price(n_clicks, apt, ec, condo, time, radius, postal_input, property_type, floor_num, floor_area, lease):
    
    if n_clicks is None:
        
        # Map 
        map_component = html.Iframe(srcDoc = open('assets/default_map.html', 'r').read(), height = '600')
        
        # Timeseries 
        
        filtered_df = prelim_ds.copy()
        filtered_df['Sale Month'] = filtered_df['Sale Date'].apply(lambda x : x.strftime('%Y-%m')) # to plot based on Year and Month
        filtered_df['Sale Year'] = filtered_df['Sale Date'].apply(lambda x : x.year) # to plot based on Year
        grp_df = filtered_df.groupby(['Sale Month', 'Planning Area']).mean().reset_index()
        
        
        fig = px.line(grp_df, 
                      x="Sale Month", 
                      y="PPI", 
                      #color='Planning Area',
                      labels = {"Sale Month":"Year", "PPI":"Property Price Index"})

        fig.update_layout(plot_bgcolor = '#f8f4f0')
        
        # To control white space surrounding the plot 
        fig.update_layout(margin={'t': 15, 'b':20, 'l':20, 'r':30})
        
        fig.update_layout(height = 450)
        
        ts_plot = dcc.Graph(figure = fig)
        
        
        # Transaction Table
        df = prelim_ds[['Sale Date', 'Address', 'Floor Number', 'Area (SQM)', 'Remaining Lease', 'Unit Price ($ PSM)']].copy()
        df = df.rename(columns ={'Area (SQM)': 'Floor Area (SQM)'})
        df = df.sort_values(by = ['Sale Date'], ascending = False).head(100)
        df['Sale Date'] = df['Sale Date'].apply(lambda x: x.date())
        
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df.columns],
            
            # Remove Pagination
            page_action='none',
            
            #For sorting by columns
            sort_action="native",
            
            # For filtering rows by column values
            filter_action="native",
            
            #style_as_list_view=True,
                        
            style_table={'max-height': '400px', 
                         'font-size': '13px'}, 
            
            style_cell = {'textAlign': 'center', 
                          'font-family': 'sans-serif', 
                          'width': '{}%'.format(len(df.columns))
                          #'minWidth': '20px', 'width': '20px', 'maxWidth': '200px'
            }, 
            
            #Controilling width of columns
            style_cell_conditional=[{'if': {'column_id': 'Sale Date'},'width': '5%'},
                                    {'if': {'column_id': 'Address'},'width': '5.5%'},],
            
            
            style_data={'padding-left': 7},
            
            #striped rows
            style_data_conditional=[{'if': {'row_index': 'even'},
                                     'backgroundColor': '#f2f2ed'
                                     #'lightgrey'
                                     }], 
            
            #Fixed row for when scrolling vertically
            fixed_rows={'headers': True}, 
            
            style_header={'backgroundColor': 'rgb(255, 255, 255)',
                          'fontWeight': 'bold',
                          'padding-left': 7},
            
            
        )
        
        transaction_table = html.Div([
            html.Div('Past 100 Recent Transactions', style = {'padding-bottom': 2, 'font-size': 'xx-large'}), 
            table
        ])
        
        return ["", 'Island Wide', transaction_features(full_sample), map_component, transaction_table, ts_plot]
   
    else: 

        ##### Current Global Listing Object #####
        global curr_listing
        curr_listing = Listing(postal_input, property_type, int(floor_num), int(floor_area), int(lease))
        
        global price_output, price_psm_output
        price_output, price_psm_output = curr_listing.pred_price("modelling/", cols, postal_code_area, area_df, sch, train, police_centre, avg_cases)

        # For testing
        #curr_listing = Listing('597592', 'Condominium', 6, 99, 70)
        #curr_listing = Listing('689527', 'Condominium', 6, 99, 70)
        
        ##### Parameters of Sample Object #####
        time_param = [0,0]
        if (time == 'Past 5 Years'): 
            time_param[0] = 1
        elif (time == 'Past 10 Years'): 
            time_param[1] = 1
            
        radius_param = [0,0]
        if (radius == 'Within 1km'):
            radius_param[0] = 1
        elif (radius == 'Within 2km'):
            radius_param[1] = 1
            
        ec_param, condo_param, apt_param = 0, 0, 0
        if ec: 
            ec_param = 1
        if condo: 
            condo_param = 1
        if apt: 
            apt_param = 1
        
        ##### Current Global Sample Object #####
        global curr_sample
        params = { 'radius' : radius_param, 
                   'property' : [ec_param, condo_param, apt_param],
                   'time' : time_param
        }
        curr_sample = Sample(params, prelim_ds)
        curr_sample.get_filtered_df(prelim_ds, curr_listing.get_lon(), curr_listing.get_lat())
        
        curr_sample.get_map(curr_listing.get_lon(), curr_listing.get_lat(), 100)
        map_component = html.Iframe(srcDoc = open('sample_map.html', 'r').read(), height = '600')
        
        transaction_table = curr_sample.get_transaction_table()
        
        psm_timeseries_plot = curr_sample.plot_psm(prelim_ds, area_df, curr_listing.get_planning_area(postal_code_area, area_df), 2)
        
        
        return [overview_section(curr_listing, price_output, price_psm_output), 
                curr_listing.get_planning_area(postal_code_area, area_df).title(), 
                transaction_features(curr_sample), 
                map_component, 
                transaction_table, 
                psm_timeseries_plot]


if __name__ == '__main__': 
    app.run_server(debug = False)
