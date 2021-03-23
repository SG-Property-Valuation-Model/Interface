# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import dash 
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

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
                                dbc.Input(style = {'font-size': 'large', 'text-align': 'center'})], 
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
                                dbc.Input(style = {'font-size': 'large', 'text-align': 'center'})], 
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
                                dbc.Input(style = {'font-size': 'large', 'text-align': 'center'}), 
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
                                dbc.Input(style = {'font-size': 'large', 'text-align': 'center'}), 
                                dbc.InputGroupAddon("Years", addon_type="append")], 
                                size="lg", 
                                style = {'width': '-webkit-fill-available'}), 
                #className="mr-3", #style = {'width': '50%'}
                ),
            width = 4
        ), 
        
        # Submit button for form
        dbc.Col(
            dbc.Button("Submit", 
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
    html.H1('Halvernia Heights'), 
    html.H2('Predicted Valuation: ' +  '$1,000,000')
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
              dash.dependencies.Input("property-dropdown-apt", "n_clicks"),],)

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

if __name__ == '__main__': 
    app.run_server(debug = False)