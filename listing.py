'''
functions to get distance to nearest train station and nearest train line are still incomplete
distance to station set as 0 for now
nearest train line set as BLUE for now
'''

import pandas as pd
import numpy as np
import geopandas as gp
from amenities import nearest_sch, nearest_police_centre, nearest_train
from location import postal_search, area_region
import joblib
import xgboost

class Listing:
    def __init__(self, postal, property_type, floor_num, floor_area, remaining_lease):
        '''
        :param postal: str, 6 characters
        :param property_type: str, Apartment/Executive Condominium/Condominium
        :param floor_num: float
        :param floor_area: float
        :param remaining_lease: float
        '''
        self.postal = postal
        self.property_type = property_type
        self.floor_num = int(floor_num)
        self.floor_area = int(floor_area)
        self.remaining_lease = int(remaining_lease)
        return

    # Get longitude of property
    def get_lon(self):
        return postal_search(self.postal)[0]

    # Get latitude of property
    def get_lat(self):
        return postal_search(self.postal)[1]

    # Get building name of property
    def get_building(self):
        return postal_search(self.postal)[2]

    # Get geometry Point of property
    def get_geom(self):
        geometry = gp.points_from_xy([self.get_lon()], [self.get_lat()])
        return geometry

    # Get planning area property is in
    def get_planning_area(self, area_centroid):
        planning_area = area_region(self.postal, area_centroid)[0]
        return planning_area

    # Get planning region property is in
    def get_planning_region(self, area_centroid):
        planning_region = area_region(self.postal, area_centroid)[1]
        return planning_region

    # Get nearest police centre to property
    def get_police_centre(self, police_centre_gdf):
        geom = self.get_geom()
        police_centre = nearest_police_centre(geom, police_centre_gdf)[1]
        return police_centre

    # Get distance to nearest police centre
    def police_centre_dist(self, police_centre_gdf):
        geom = self.get_geom()
        centre_dist = nearest_police_centre(geom, police_centre_gdf)[0]
        return centre_dist

    # Get average number of cases per year for nearest police centre to property
    def get_centre_avg_cases(self, police_centre_gdf, avg_cases_by_npc):
        police_centre = self.get_police_centre(police_centre_gdf)
        avg_case = int(avg_cases_by_npc[avg_cases_by_npc['Police Centre'] == police_centre]['Average Cases Per Year'].values[0])
        return avg_case

    # Get distance to nearest train station
    def train_dist(self, train_gdf):
        geom = self.get_geom()
        nearest_dist = nearest_train(geom, train_gdf)[0]
        return nearest_dist

    # Get train stations within 1km
    def train_stations(self, train_gdf):
        geom = self.get_geom()
        stations = nearest_train(geom, train_gdf)[2]
        return stations

    # Get lines within 1km
    def train_lines(self, train_gdf):
        geom = self.get_geom()
        lines = nearest_train(geom, train_gdf)[1]
        return lines

    # Get distance to nearest school
    def sch_dist(self, sch_gdf):
        geom = self.get_geom()
        nearest_dist = nearest_sch(geom, sch_gdf)[1]
        return nearest_dist

    # Get nearest school name
    def sch_name(self, sch_gdf):
        geom = self.get_geom()
        name = nearest_sch(geom, sch_gdf)[0]
        return name

    # create dataframe containing property details to be used for prediction
    def convert_to_df(self, main_df_col, area_centroids, sch_gdf, train_gdf, police_centre_gdf, avg_cases_by_npc): # parse in list of training df col because predict df needs to be in same order
        # Create dataframe for property for prediction
        df = pd.DataFrame(columns=main_df_col, index=range(1))
        df['Area (SQM)'] = self.floor_area
        df['Floor Number'] = self.floor_num
        df['PPI'] = 153.3 #2020 Q4 PPI
        df['Average Cases Per Year'] = self.get_centre_avg_cases(police_centre_gdf, avg_cases_by_npc)
        df['Nearest Primary School'] = self.sch_dist(sch_gdf)
        df['nearest_station_distance'] = self.train_dist(train_gdf)
        df['Remaining Lease'] = self.remaining_lease

        # if the column(s) is not the base dummy column that got dropped
        if self.get_planning_area(area_centroids) in main_df_col:
            df[self.get_planning_area(area_centroids)] = 1
        if self.property_type in main_df_col:
            df[self.property_type] = 1
        # property can have more than 1 line within 1km radius
        lines = self.train_lines(train_gdf)
        for i in lines:
            if i in main_df_col:
                df[i] = 1

        # for remaining one-hot encoded columns that are Nan, replace with 0
        df = df.fillna(0)
        return df

    def pred_psm(self, path, main_df_col, area_centroids, sch_gdf, train_gdf, police_centre_gdf, avg_cases_by_npc):
        property_df = self.convert_to_df(main_df_col, area_centroids, sch_gdf, train_gdf, police_centre_gdf, avg_cases_by_npc)
        s_scaler = joblib.load(path + 'standard_scaler.bin')
        mm_scaler = joblib.load(path + 'mm_scaler.bin')
        standardScale_vars = ['Area (SQM)',
                              'Floor Number',
                              'PPI',
                              'Average Cases Per Year',
                              'Nearest Primary School',
                              'nearest_station_distance']
        minMax_vars = ['Remaining Lease']
        s_scaled = pd.DataFrame(s_scaler.transform(property_df.loc[:, standardScale_vars].copy()),
                                columns=standardScale_vars)
        mm_scaled = pd.DataFrame(mm_scaler.transform(property_df.loc[:, minMax_vars].copy()), columns=minMax_vars)

        property_df_scaled = pd.concat([s_scaled,
                        mm_scaled,
                        property_df.loc[:, 'Ang Mo Kio':'Executive Condominium'].copy()], axis=1)
        model = joblib.load(path + 'model_test.pkl')
        # Use the loaded model to make predictions
        prediction = model.predict(property_df_scaled)[0]
        return prediction


    def pred_price(self, path, main_df_col, area_centroids, sch_gdf, train_gdf, police_centre_gdf, avg_cases_by_npc):
        '''
        :param path: takes in path where model weights and scalers are stored
        :param main_df_col: list of training dataset column names so that prediction df tallies
        :param area_centroids: to get the planning area property is in
        :param sch_gdf: to get nearest school distance
        :param police_centre_gdf: to get nearest police centre
        :param avg_cases_by_npc: to get avg crime cases per year for nearest police centre
        :return: predicted price of unit and predicted price per sqm
        '''
        predicted_psm = self.pred_psm(path, main_df_col, area_centroids, sch_gdf, train_gdf, police_centre_gdf, avg_cases_by_npc)
        unit_price = self.floor_area * predicted_psm
        return unit_price, predicted_psm

'''
# TESTING
#Input postal code, property type, floor num, sqm, remaining lease
property = Listing('098656', 'Condominium', 6, 99, 70)
sch = pd.read_csv('datasets/primary_sch_gdf.csv')
train = pd.read_csv('datasets/train_gdf.csv')
area_df = pd.read_csv('datasets/area_centroid.csv')
modelling = pd.read_csv('datasets/modelling_dataset.csv')
police_centre = pd.read_csv('datasets/police_centre_gdf.csv')
avg_cases = pd.read_csv('datasets/average_cases_by_npc.csv')
cols = list(modelling.columns)
cols.remove('Unit Price ($ PSM)')
print(cols)
print(property.get_lat())
print(property.get_lon())
print(property.get_geom())
print(property.get_planning_area(area_df))
print(property.get_planning_region(area_df))
print(property.train_lines(train))
print(property.train_dist(train))
print(property.train_stations(train))
print(property.sch_dist(sch))
print(property.sch_name(sch))
print(property.get_police_centre(police_centre))
print(property.police_centre_dist(police_centre))
print(property.get_centre_avg_cases(police_centre, avg_cases))
print(property.convert_to_df(cols, area_df, sch, train, police_centre, avg_cases))
print(property.pred_price('modelling/', cols, area_df, sch, train, police_centre, avg_cases))
'''