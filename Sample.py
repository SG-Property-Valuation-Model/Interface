#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 15:29:35 2021

@author: triciachia
"""

import pandas as pd
import numpy as np
import dash
import datetime
import folium
import dash_table
from math import radians, cos, sin, asin, sqrt


class Sample:
    def __init__(self, params):
        self.radius = params['radius']
        self.property = params['property']
        self.time = params['time']
        self.dataframe = None
        
    def get_radius(self): # take furthest as filter
        if sum(self.radius) == 2:
            radius = 2
        else:
            if self.radius[0] == 1:
                radius = 1
            elif self.radius[1] == 1:
                radius = 2
            else: # no input, then set to minimum
                radius = 1
        return radius
    
    def get_time(self): # take latest as filter, if not input take for past year
        if sum(self.time) == 2:
            time = 10
        else:
            if self.time[0] == 1:
                time = 5
            elif self.time[1] == 1:
                time = 10
            else: # no input, set to minimum 
                time = 1
        return time
    
    def get_property(self):
        property_type = []
        if self.property[0] == 1:
            property_type.append('Executive Condominium')
            
        if self.property[1] == 1:
            property_type.append('Condominium')
            
        if self.property[2] == 1:
            property_type.append('Apartment')
        return property_type

    def get_filtered_df(self, data, listing_long, listing_lat):
        def haversine(lon1, lat1, lon2, lat2): # find distance between 2 lisitng
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

            # haversine formula 
            dlon = lon2 - lon1 
            dlat = lat2 - lat1 
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a)) 
            r = 6371 # Radius of earth in kilometers. Use 3956 for miles
            return c * r
        
        radius = self.get_radius()
        time = self.get_time()
        property_type = self.get_property()
        start_date = (datetime.datetime.now() - datetime.timedelta(days=time*365)).strftime('%m/%d/%Y')
        end_date = datetime.datetime.now().strftime('%m/%d/%Y')
        interm_df = data[(data['Sale Date']>= start_date) & (data['Sale Date']< end_date) & (data['Property Type'].isin(property_type))]

        #find within radius
        interm_df['distance'] = np.nan

        for index, row in interm_df.iterrows():
            long = row['LONGITUDE']
            lat = row['LATITUDE']
            # calculate distance between this and query point
            interm_df.loc[index, 'distance'] =  haversine(listing_long, listing_lat, long, lat)

        filtered_df = interm_df[interm_df['distance'] <= radius]
        self.dataframe = filtered_df
        #return filtered_df
    
    def get_transaction_table(self, listing_long,  listing_lat):
        df =  self.dataframe
        df = df[['Sale Date', 'Address', 'Floor Number', 'Remaining Lease', 'Unit Price ($ PSM)']]
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df.columns],

        style_cell_conditional=[
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['Date', 'Region']
        ],
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
            }
        )
        return table
    
    def get_map(self, listing_long, listing_lat, limit):
        listing_coord = (listing_lat,listing_long)
        df = self.dataframe.sample(limit) # get a random sample to show on map, might duplicated markers
        
        df_coord = df[['LATITUDE', 'LONGITUDE', 'BUILDING', 'Planning Area']]
        m = folium.Map(location = listing_coord, zoom_start=15)
        
        # add markers
        for index, row in df_coord.iterrows():
            long = row['LONGITUDE']
            lat = row['LATITUDE']
            pop_up = folium.Marker(
                location=[lat, long],
                popup="<i>" + row['BUILDING']+ ','+ row['Planning Area']+"</i>", 
            ).add_to(m)
            
        # return html object
        m.save('sample_map.html')


