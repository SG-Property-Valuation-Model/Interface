#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import dash
import datetime
import folium
import dash_table
import plotly.express as px
import dash_core_components as dcc
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2): # find distance between 2 lisitng
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

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
    
    def get_time(self): # take latest as filter
        if sum(self.time) == 2:
            time = 10
        else:
            if self.time[0] == 1:
                time = 5
            elif self.time[1] == 1:
                time = 10
            else: # no input, set to minimum, past 1 year 
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
        '''
        Parameters
        - data: Dataframe with all historical listing; Preliminary dataset
        - listing_long: Longitude of listing
        - lisiting_lat: Latitude of listing
        '''
        radius = self.get_radius()
        time = self.get_time()
        property_type = self.get_property()
        
        # convert listing longitude and latitude to float
        listing_long = float(listing_long)
        listing_lat = float(listing_lat)
        
        #start_date = (datetime.datetime.now() - datetime.timedelta(days=time*365)).strftime('%m/%d/%Y')
        start_date = (datetime.datetime.now() - datetime.timedelta(days=time*365)).strftime('%Y-%m-%d')
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        interm_df = data[(data['Sale Date']>= start_date) & (data['Sale Date']< end_date) & (data['Property Type'].isin(property_type))]

        #find past listings within radius
        interm_df['distance'] = np.nan

        for index, row in interm_df.iterrows():
            long = row['LONGITUDE']
            lat = row['LATITUDE']
            # calculate distance between this and query point
            interm_df.loc[index, 'distance'] =  haversine(listing_long, listing_lat, long, lat)

        filtered_df = interm_df[interm_df['distance'] <= radius]
        self.dataframe = filtered_df
        #return filtered_df
    
    def get_transaction_table(self):
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
        
        '''
        Parameters
        - listing_long: Longitude of listing
        - lisiting_lat: Latitude of listing
        - limit: Maximum number of points to show on map
        '''
        # convert listing longitude and latitude to float
        listing_long = float(listing_long)
        listing_lat = float(listing_lat)
        
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
        
    def get_closest_planning_area(self, area_centroids, listing_PA, num_of_closest = 2):
        '''
        Parameters
        - area_centroids: Dataframe consisting the coordinates of centroid for each planning area
        - listing_PA: Planning Area of listing 
        - num_of_closest: N number of Planning Area closest to that of listing, default is 2.
        '''
        # change to upper case
        listing_PA = listing_PA.upper()
        # get longitude and latitude of the centroid for listing's planning area
        centroid_long = area_centroids[area_centroids['Planning Area'] == listing_PA]['Centroid Longitude']
        centroid_lat = area_centroids[area_centroids['Planning Area'] == listing_PA]['Centroid Latitude']
        closest_PA = {}
        for index, row in area_centroids.iterrows():
            if row['Planning Area'] == listing_PA:
                continue
            else:
                # find distance between 2set of coordinates using Haversine
                PA_long = row['Centroid Longitude']
                PA_lat = row['Centroid Latitude']
                closest_PA[row['Planning Area']] = haversine(centroid_long, centroid_lat, PA_long, PA_lat)
                
        # get the closest N Planning Area       
        sorted_list = sorted(closest_PA.items(), key = lambda kv: kv[1])
        final_closest = list(map(lambda x: x[0], sorted_list[:num_of_closest]))
        
        return final_closest
    
    def plot_psm(self, historical_df, area_centroids, listing_PA, num_of_closest = 2):
        '''
        Parameters
        - historical_df: Dataframe consisting of all historical transactions; preliminary dataset
        - area_centroids: Dataframe consisting the coordinates of centroid for each planning area
        - listing_PA: Planning Area of listing 
        - num_of_closest: N number of Planning Area closest to that of listing, default is 2.
        '''
        
        # get the closest Planning area
        closest_PA = self.get_closest_planning_area(area_centroids, listing_PA, num_of_closest = 2)
        closest_PA.append(listing_PA)
        print(closest_PA)
        # get data based on time and property type filter, radius not applicable since we are filtering based on closest areas
        time = self.get_time()
        property_type = self.get_property()
        
        start_date = (datetime.datetime.now() - datetime.timedelta(days=time*365)).strftime('%Y-%m-%d')
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        filtered_df = historical_df[(historical_df['Sale Date']>= start_date) & (historical_df['Sale Date']< end_date) & (historical_df['Property Type'].isin(property_type))& (historical_df['Planning Area'].isin(closest_PA))][['Sale Date', 'Planning Area','Unit Price ($ PSM)']]
        print(filtered_df['Planning Area'].value_counts())
        # Group data to find the mean PSM price
        filtered_df['Sale Month'] = filtered_df['Sale Date'].apply(lambda x : x.strftime('%Y-%m')) # to plot based on Year and Month
        filtered_df['Sale Year'] = filtered_df['Sale Date'].apply(lambda x : x.year) # to plot based on Year
        grp_df = filtered_df.groupby(['Sale Month', 'Planning Area']).mean().reset_index()
        print(grp_df['Planning Area'].value_counts())
        # plot timeseries 
        ts_plot = dcc.Graph(id='historical_timeseries', 
                            figure = px.line(grp_df, x="Sale Month", y="Unit Price ($ PSM)", color='Planning Area',
                             labels = {"Sale Month":"Year", "Unit Price ($ PSM)":"Average Unit Price ($ PSM)"})
                            )
        return ts_plot
        
        

'''
TESTING
params = {
    'radius' : [0,1], 
    'property' : [1,1,1],
    'time' : [1,0],
 }
data = pd.read_csv('datasets/preliminary_dataset.csv')
data['Sale Date'] = pd.to_datetime(data['Sale Date'], format='%Y-%m-%d')
#data['Planning Area'] = data['Planning Area'].apply(lambda x: x.upper())

area_df = pd.read_csv('datasets/area_centroid.csv')
limit = 50
try_index = 9
listing_lat = data.loc[try_index]['LATITUDE']
listing_long = data.loc[try_index]['LONGITUDE']
listing_PA = data.loc[try_index]['Planning Area']
sample_instance = Sample(params)
sample_instance.get_filtered_df(data, listing_long, listing_lat)
print(sample_instance.dataframe.shape)
print('max dist' + str(sample_instance.dataframe['distance'].max()))
print('min year' + str(sample_instance.dataframe['Sale Date'].min()))     
print('ppt' + str(sample_instance.dataframe['Property Type'].unique()))
#sample_instance.get_map(listing_long, listing_lat, limit) 
print(sample_instance.get_closest_planning_area(area_df, listing_PA,2))
sample_instance.plot_psm(data, area_df, listing_PA, 2)

# try with listing
import listing
postal_input = '538683'
property_type = 'Condominium'
floor_num = 3
floor_area = 91
lease = 78
try_unit = listing.Listing(postal_input, property_type, floor_num, floor_area, lease)
listing_lat = try_unit.get_lat()
listing_long = try_unit.get_lon()
listing_PA = try_unit.get_planning_area(area_df)
print(listing_PA)
sample_instance2 = Sample(params)
sample_instance2.get_filtered_df(data, listing_long, listing_lat)
print(sample_instance2.dataframe.shape)
print('max dist' + str(sample_instance2.dataframe['distance'].max()))
print('min year' + str(sample_instance2.dataframe['Sale Date'].min()))     
print('ppt' + str(sample_instance2.dataframe['Property Type'].unique()))
#sample_instance.get_map(listing_long, listing_lat, limit) 
print(sample_instance2.get_closest_planning_area(area_df, listing_PA,2))
sample_instance2.plot_psm(data, area_df, listing_PA, 2)'''
