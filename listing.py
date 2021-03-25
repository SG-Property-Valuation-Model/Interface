'''
functions to get distance to nearest train station and nearest train line are still incomplete
distance to station set as 0 for now
nearest train line set as BLUE for now
'''

import pandas as pd
import numpy as np
import geopandas as gp
from school import nearest_sch
from location import postal_search, area_region
import joblib
from sklearn.preprocessing import StandardScaler, MinMaxScaler

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

    def get_lon(self):
        return postal_search(self.postal)[0]

    def get_lat(self):
        return postal_search(self.postal)[1]

    def get_building(self):
        return postal_search(self.postal)[2]

    def get_geom(self):
        geometry = gp.points_from_xy([self.get_lon()], [self.get_lat()])
        return geometry

    def get_planning_area(self, area_centroid):
        planning_area = area_region(self.postal, area_centroid)[0]
        return planning_area

    def get_planning_region(self, area_centroid):
        planning_region = area_region(self.postal, area_centroid)[1]
        return planning_region

    # not done
    def train_dist(self):
        return 0

    # not done
    def get_mrt_line(self):
        return 'BLUE'

    def sch_dist(self, sch_gdf):
        geom = self.get_geom()
        nearest_dist = nearest_sch(geom, sch_gdf, 2000)
        return nearest_dist

    # create dataframe containing property details to be used for prediction
    def convert_to_df(self, main_df_col, area_centroids, sch_gdf): # parse in list of training df col because predict df needs to be in same order

        col_lowercase = [x.lower() for x in main_df_col]
        # Create dataframe for property for prediction
        df = pd.DataFrame(columns=col_lowercase, index=range(1))
        df['area (sqm)'] = self.floor_area
        df['floor number'] = self.floor_num
        df['ppi'] = 153.3 #KIV
        df['average cases per year'] = 0 #KIV???
        df['nearest primary school'] = self.sch_dist(sch_gdf)
        df['nearest_station_distance'] = self.train_dist()
        df['remaining lease'] = self.remaining_lease

        # if the column(s) is not the base dummy column that got dropped
        if self.get_planning_area(area_centroids).lower() in col_lowercase:
            df[self.get_planning_area(area_centroids).lower()] = 1
        if self.property_type.lower() in col_lowercase:
            df[self.property_type.lower()] = 1
        if self.get_mrt_line().lower() in col_lowercase:
            df[self.get_mrt_line().lower()] = 1

        # for remaining one-hot encoded columns that are Nan, replace with 0
        df = df.fillna(0)
        return df

    def pred_psm(self, path, main_df_col, area_centroids, sch_gdf):
        property_df = self.convert_to_df(main_df_col, area_centroids, sch_gdf)
        s_scaler = joblib.load(path + 'standard_scaler.bin')
        mm_scaler = joblib.load(path + 'mm_scaler.bin')
        standardScale_vars = ['area (sqm)',
                              'floor number',
                              'ppi',
                              'average cases per year',
                              'nearest primary school',
                              'nearest_station_distance']
        minMax_vars = ['remaining lease']
        s_scaled = pd.DataFrame(s_scaler.transform(property_df.loc[:, standardScale_vars].copy()),
                                columns=standardScale_vars)
        mm_scaled = pd.DataFrame(mm_scaler.transform(property_df.loc[:, minMax_vars].copy()), columns=minMax_vars)

        property_df_scaled = pd.concat([s_scaled,
                        mm_scaled,
                        property_df.loc[:, 'ang mo kio':'executive condominium'].copy()], axis=1)
        model = joblib.load(path + 'model_test.pkl')
        # Use the loaded model to make predictions
        prediction = model.predict(property_df_scaled)[0]
        return prediction


    def pred_price(self, path, main_df_col, area_centroids, sch_gdf):
        '''
        :param path: takes in path where model weights and scalers are stored
        :param main_df_col: list of training dataset column names so that prediction df tallies
        :param area_centroids: to get the planning area property is in
        :param sch_gdf: to get nearest school distance
        :return: predicted price of unit and predicted price per sqm
        '''
        predicted_psm = self.pred_psm(path, main_df_col, area_centroids, sch_gdf)
        print('floor:', self.floor_area)
        print(type(self.floor_area))
        print('predict:', predicted_psm)
        unit_price = self.floor_area * predicted_psm
        return unit_price, predicted_psm

'''
property = Listing('098656', 'Condominium', 6, 99, 35)
sch = pd.read_csv('C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Final Merge of Data/primary_sch_gdf.csv')
area_df = pd.read_csv('C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Interface/area_centroid.csv')
modelling = pd.read_csv('C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Modelling/modelling_dataset.csv')
cols = list(modelling.columns)
cols.remove('Unit Price ($ PSM)')
print(cols)
print(property.get_lat())
print(property.get_lon())
print(property.get_geom())
print(property.get_planning_area(area_df))
print(property.get_planning_region(area_df))
print(property.sch_dist(sch))
print(property.convert_to_df(cols, area_df, sch))
print(property.pred_price('C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Modelling/', cols, area_df, sch))
'''