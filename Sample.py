#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from pandas.api.types import is_string_dtype
import numpy as np
import dash
import datetime
import folium
import dash_table
import plotly.express as px
import plotly.graph_objects as go
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
    def __init__(self, params, data):
        self.radius = params['radius']
        self.property = params['property']
        self.time = params['time']
        self.dataframe = data
        
    def get_radius(self): # take furthest as filter
        if sum(self.radius) == 2:
            radius = 2
        else:
            if self.radius[0] == 1:
                radius = 1
            elif self.radius[1] == 1:
                radius = 2
            else: # no input, then set to maximum
                radius = 2
        return radius
    
    def get_time(self): # take latest as filter
        if sum(self.time) == 2:
            time = 10
        else:
            if self.time[0] == 1:
                time = 5
            elif self.time[1] == 1:
                time = 10
            else: # no input, set to minimum, past 20 years 
                time = 5
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
        - listing_lat: Latitude of listing
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
        interm_df['distance'] = interm_df.apply(lambda x: haversine(listing_long, listing_lat, x['LONGITUDE'], x['LATITUDE']), axis = 1)
        
        filtered_df = interm_df[interm_df['distance'] <= radius]
        self.dataframe = filtered_df
        #return filtered_df
        
    def get_average_psf(self):
        if (is_string_dtype(self.dataframe['Unit Price ($ PSF)'])):
            self.dataframe['Unit Price ($ PSF)'] = self.dataframe['Unit Price ($ PSF)'].apply(lambda x: int(x.replace(',', "")))
        return round(self.dataframe['Unit Price ($ PSF)'].mean(),2)
    
    def get_average_floor_area(self):
        # Average floor area in SQFT
        return round(self.dataframe['Area (SQFT)'].mean(),2)
    
    def get_total_transactions(self):
        return self.dataframe.shape[0]
    
    def get_transaction_table(self):
        
        df =  self.dataframe.copy()
        df = df[['Sale Date', 'address_trunc', 'BUILDING','Floor Number', 'Area (SQFT)', 'Remaining Lease', 'Unit Price ($ PSF)']].copy()
        df.rename(columns = {'Area (SQFT)': 'Floor Area', 'address_trunc': 'Address', 'BUILDING': 'Building Name'}, inplace = True)
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
            }, 
            
            
            style_data={'padding-left': 7},
            
            #striped rows
            style_data_conditional=[{'if': {'row_index': 'even'},
                                     'backgroundColor': '#ebe9e6'#'#f2f2ed'
                                     #'lightgrey'
                                     }], 
            
            #Fixed row for when scrolling vertically
            fixed_rows={'headers': True}, 
            
            style_header={'backgroundColor': 'rgb(255, 255, 255)',
                          'fontWeight': 'bold',
                          'padding-left': 7},
            
            
        )
        
        return table
    
    def get_map(self, listing_long, listing_lat, listing_price_psm_output, listing_building_name, listing_address, limit = 50):
        '''
        Parameters
        - listing_long: Longitude of listing
        - listing_lat: Latitude of listing
        - limit: Maximum number of points to show on map, default = 50
        '''
        # convert listing longitude and latitude to float
        listing_long = float(listing_long)
        listing_lat = float(listing_lat)
        listing_coord = (listing_lat,listing_long)
        
        # get the filtered dataframe
        df = self.dataframe[['LATITUDE', 'LONGITUDE', 'BUILDING', 'Unit Price ($ PSF)', 'address_trunc']]
        
        # group the transactions
        grp_df = df.groupby(['LATITUDE', 'LONGITUDE', 'BUILDING', 'address_trunc']).agg(avg_psm=('Unit Price ($ PSF)', 'mean'),
                                                                       num_transactions =('Unit Price ($ PSF)', 'count')).reset_index()
        grp_df['avg_psm'] = grp_df['avg_psm'].apply(lambda x: round(x,2))
        
        # check if filtered data has past transactions of the same listing, get the number of past transactions
        if len(grp_df[(grp_df['LATITUDE'] == listing_lat) & (grp_df['LONGITUDE'] == listing_long)]) > 0:
            num_past_transactions = grp_df[(grp_df['LATITUDE'] == listing_lat) & (grp_df['LONGITUDE'] == listing_long)].iloc[0]['num_transactions']
            avg_psm = grp_df[(grp_df['LATITUDE'] == listing_lat) & (grp_df['LONGITUDE'] == listing_long)].iloc[0]['avg_psm']
        else: 
            num_past_transactions = 0 
            avg_psm = 'Not Available'
        
        # limit the number of points shown on the map
        if len(grp_df) > limit :
            grp_df = grp_df.sample(limit)
        else:
            grp_df = grp_df
            
        m = folium.Map(location = listing_coord, zoom_start=14)

        # add markers
        for index, row in grp_df.iterrows():
            long = row['LONGITUDE']
            lat = row['LATITUDE']
            
            pop_up_text = "<H4>" + row['BUILDING'] + "</H4>" + row['address_trunc'] + "<br>" + "<b>Average Unit Price ($ PSF): <b>" + str(row['avg_psm']) + "<br>" + "<b>Number of Past Transactions: <b>" + str(row['num_transactions'])

            if (long == listing_long) & (lat == listing_lat):
                continue 
            else: 
                
                pop_up = folium.Marker(
                                location=[lat, long],
                                popup = folium.Popup(pop_up_text, 
                                                     min_width = 250, max_width = 250),
                                icon = folium.Icon(color= 'darkblue')
                        ).add_to(m)
        
        # adding marker for listing in red
        pop_up_text = "<H4>" + listing_building_name + "</H4>"  + listing_address + "<br>" + "<b>Average Unit Price ($ PSF): <b>" + str(avg_psm) + "<br>" + "<b>Number of Past Transactions: <b>" + str(num_past_transactions)
        
        pop_up = folium.Marker(
                        location=[listing_lat, listing_long],
                        popup= folium.Popup(pop_up_text, 
                                                     min_width = 250, max_width = 250),
                        icon = folium.Icon(color='red')
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
        
        closest_PA = area_centroids[area_centroids['Planning Area'] != listing_PA].copy()
        closest_PA['distance'] = closest_PA.apply(lambda x: haversine(centroid_long, centroid_lat, x['Centroid Longitude'], x['Centroid Latitude'] ), axis = 1)
        
        return closest_PA.sort_values('distance', ascending = True).head(num_of_closest)['Planning Area'].tolist()
        
        
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
        #print(closest_PA)
        
        # get data based on time and property type filter, radius not applicable since we are filtering based on closest areas
        time = self.get_time()
        property_type = self.get_property()
        
        start_date = (datetime.datetime.now() - datetime.timedelta(days=time*365)).strftime('%Y-%m-%d')
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Convert Planning Area to Upper Case
        historical_df['Planning Area'] = historical_df['Planning Area'].apply(lambda x: x.upper())
        filtered_df = historical_df[(historical_df['Sale Date']>= start_date) & (historical_df['Sale Date']< end_date) & (historical_df['Property Type'].isin(property_type))& (historical_df['Planning Area'].isin(closest_PA))][['Sale Date', 'Planning Area','Unit Price ($ PSF)']]
        #print(filtered_df['Sale Date'].dtypes)
        #print(filtered_df['Planning Area'].unique())
        
        # Group data to find the mean PSF price
        filtered_df['Sale Month'] = filtered_df['Sale Date'].apply(lambda x : x.strftime('%Y-%m')) # to plot based on Year and Month
        filtered_df['Sale Year'] = filtered_df['Sale Date'].apply(lambda x : x.year) # to plot based on Year
        grp_df = filtered_df.groupby(['Sale Month', 'Planning Area']).mean().reset_index()
        #print(grp_df['Planning Area'].unique())
        
        # plot timeseries 
        fig = px.line(grp_df, 
                      x="Sale Month", 
                      y="Unit Price ($ PSF)", 
                      color='Planning Area',
                      labels = {"Sale Month":"Year", "Unit Price ($ PSF)":"Average Unit Price ($ PSF)"})

        fig.update_layout(plot_bgcolor = '#f8f4f0')
        
        # To control white space surrounding the plot 
        fig.update_layout(margin={'t': 15, 'b':20, 'l':20, 'r':30})
        
        fig.update_layout(height = 450)
        
        ts_plot = dcc.Graph(figure = fig)
    
        return ts_plot
        
        


### TESTING
"""
params = {
    'radius' : [0,1], 
    'property' : [1,1,1],
    'time' : [1,1],
 }
data = pd.read_csv('datasets/preliminary_dataset.csv')
data['Sale Date'] = pd.to_datetime(data['Sale Date'], format='%Y-%m-%d')
#data['Planning Area'] = data['Planning Area'].apply(lambda x: x.upper())

#start_date = (datetime.datetime.now() - datetime.timedelta(days=time*365)).strftime('%Y-%m-%d')
#end_date = datetime.datetime.now().strftime('%Y-%m-%d')
print(data['Planning Area'].unique())
closest_PA = ['JURONG EAST', 'BUKIT TIMAH', 'CLEMENTI']
filtered_df = data[(data['Planning Area'].isin(closest_PA))][['Sale Date', 'Planning Area','Unit Price ($ PSF)']]

area_df = pd.read_csv('datasets/area_centroid.csv')
limit = 50
try_index = 1
listing_lat = data.loc[try_index]['LATITUDE']
listing_long = data.loc[try_index]['LONGITUDE']
listing_PA = data.loc[try_index]['Planning Area']
listing_building_name =  data.loc[try_index]['BUILDING']
print(listing_PA, listing_lat, listing_long)
listing_price_psm_output = 1000
sample_instance = Sample(params,data)
sample_instance.get_filtered_df(data, listing_long, listing_lat)
print(sample_instance.dataframe.shape)
print('max dist' + str(sample_instance.dataframe['distance'].max()))
print('min year' + str(sample_instance.dataframe['Sale Date'].min()))     
print('ppt' + str(sample_instance.dataframe['Property Type'].unique()))
print('avg psm:' + str(sample_instance.get_average_psm()))
print('avg floor area:' + str(sample_instance.get_average_floor_area()))
print('N transactions:' + str(sample_instance.get_total_transactions()))
sample_instance.get_map(listing_long, listing_lat, listing_price_psm_output,listing_building_name,1)  
print(sample_instance.get_closest_planning_area(area_df, listing_PA,2))
#sample_instance.plot_psm(data, area_df, listing_PA, 2)


# try with listing
import listing
params = {
    'radius' : [0,1], 
    'property' : [1,1,1],
    'time' : [1,1],
 }
data = pd.read_csv('datasets/preliminary_dataset.csv')
postal_code_area = pd.read_csv('datasets/historical_postal_code_area.csv')
postal_code_area['Postal Code'] = postal_code_area['Postal Code'].apply(lambda x: str(x).zfill(6))
police_centre = pd.read_csv('datasets/police_centre_gdf.csv')
avg_cases = pd.read_csv('datasets/average_cases_by_npc.csv')
data['Sale Date'] = pd.to_datetime(data['Sale Date'], format='%Y-%m-%d')
area_df = pd.read_csv('datasets/area_centroid.csv')
postal_input = '098656'
property_type = 'Condominium'
floor_num = 6
floor_area = 99
lease = 78
try_unit = listing.Listing(postal_input, property_type, floor_num, floor_area, lease)
listing_lat = try_unit.get_lat(postal_code_area)
listing_long = try_unit.get_lon(postal_code_area)
listing_building_name = try_unit.get_building()
listing_price_psm_output = 10000
listing_PA = try_unit.get_planning_area(data, area_df)
print(listing_PA, listing_lat, listing_long)
print(try_unit.get_police_centre(police_centre, postal_code_area))
print(try_unit.police_centre_dist(police_centre, postal_code_area))
print(try_unit.get_centre_avg_cases(police_centre, avg_cases, postal_code_area))
sample_instance2 = Sample(params,data)
sample_instance2.get_filtered_df(data, listing_long, listing_lat)
print(sample_instance2.dataframe.shape)
print('max dist' + str(sample_instance2.dataframe['distance'].max()))
print('min year' + str(sample_instance2.dataframe['Sale Date'].min()))     
print('ppt' + str(sample_instance2.dataframe['Property Type'].unique()))
print('avg psm:' + str(sample_instance2.get_average_psm()))
print('avg floor area:' + str(sample_instance2.get_average_floor_area()))
print('N transactions:' + str(sample_instance2.get_total_transactions()))
sample_instance2.get_map(listing_long, listing_lat, listing_price_psm_output,listing_building_name,1) 
#print(sample_instance2.get_closest_planning_area(area_df, listing_PA,2))
#sample_instance2.plot_psm(data, area_df, listing_PA, 2)'''
"""