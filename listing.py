import pandas as pd
import numpy as np
import geopandas as gp
from amenities import nearest_sch, nearest_police_centre, nearest_train
from location import postal_search, area_region
import joblib
import xgboost
from xgboost import XGBRegressor

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

    # Get postal code of property
    def get_postal_code(self):
        return self.postal

    # Get property type of property
    def get_property_type(self):
        return self.property_type

    # Get floor number of property
    def get_floor_num(self):
        return self.floor_num

    # Get floor area of property
    def get_floor_area(self):
        return self.floor_area

    # Get remaining lease of property
    def get_remaining_lease(self):
        return self.remaining_lease

    # Get longitude of property
    def get_lon(self, historical_df):
        historical_df['Postal Code'] = historical_df['Postal Code'].apply(lambda x: str(x).zfill(6))
        if self.postal in historical_df['Postal Code'].tolist():
            lon = historical_df[historical_df['Postal Code'] == self.postal]['LONGITUDE'].values[0]
        else:
            lon = postal_search(self.postal)[0]
        return lon

    # Get latitude of property
    def get_lat(self, historical_df):
        historical_df['Postal Code'] = historical_df['Postal Code'].apply(lambda x: str(x).zfill(6))
        if self.postal in historical_df['Postal Code'].tolist():
            lat = historical_df[historical_df['Postal Code'] == self.postal]['LATITUDE'].values[0]
        else:
            lat = postal_search(self.postal)[1]
        return lat

    # Get building name of property
    def get_building(self):
        return postal_search(self.postal)[2]

    # Get geometry Point of property
    def get_geom(self, historical_df):
        geometry = gp.points_from_xy([self.get_lon(historical_df)], [self.get_lat(historical_df)])
        return geometry

    # Get road name property is at 
    def get_road_name(self):
        return postal_search(self.postal)[3]

    # Get planning area property is in
    def get_planning_area(self, historical_df, area_centroid):
        historical_df['Postal Code'] = historical_df['Postal Code'].apply(lambda x: str(x).zfill(6))
        # Postal code is in our dataset
        if self.postal in historical_df['Postal Code'].tolist():
            planning_area = historical_df[historical_df['Postal Code'] == self.postal]['Planning Area'].values[0]
        else:
            planning_area = area_region(self.postal, area_centroid)[0]
        return planning_area

    # Get planning region property is in
    def get_planning_region(self, historical_df, area_centroid):
        historical_df['Postal Code'] = historical_df['Postal Code'].apply(lambda x: str(x).zfill(6))
        # Postal code is in our dataset
        if self.postal in historical_df['Postal Code'].tolist():
            planning_region = historical_df[historical_df['Postal Code'] == self.postal]['Planning Region'].values[0]
        else:
            planning_region = area_region(self.postal, area_centroid)[1]
        return planning_region

    # Get nearest police centre to property
    def get_police_centre(self, police_centre_gdf, historical_df):
        geom = self.get_geom(historical_df)
        police_centre = nearest_police_centre(geom, police_centre_gdf)[1]
        return police_centre

    # Get distance to nearest police centre
    def police_centre_dist(self, police_centre_gdf, historical_df):
        geom = self.get_geom(historical_df)
        centre_dist = nearest_police_centre(geom, police_centre_gdf)[0]
        return centre_dist

    # Get average number of cases per year for nearest police centre to property
    def get_centre_avg_cases(self, police_centre_gdf, avg_cases_by_npc, historical_df):
        police_centre = self.get_police_centre(police_centre_gdf, historical_df)
        avg_case = int(avg_cases_by_npc[avg_cases_by_npc['Police Centre'] == police_centre]['Average Cases Per Year'].values[0])
        return avg_case

    # Get distance to nearest train station
    def train_dist(self, train_gdf, historical_df):
        geom = self.get_geom(historical_df)
        nearest_dist = nearest_train(geom, train_gdf)[0]
        return nearest_dist

    # Get train stations within 1km
    def train_stations(self, train_gdf, historical_df):
        geom = self.get_geom(historical_df)
        stations = nearest_train(geom, train_gdf)[2]
        return stations

    # Get lines within 1km
    def train_lines(self, train_gdf, historical_df):
        geom = self.get_geom(historical_df)
        lines = nearest_train(geom, train_gdf)[1]
        return lines

    # Get distance to nearest school
    def sch_dist(self, sch_gdf, historical_df):
        geom = self.get_geom(historical_df)
        nearest_dist = nearest_sch(geom, sch_gdf)[1]
        return nearest_dist

    # Get nearest school name
    def sch_name(self, sch_gdf, historical_df):
        geom = self.get_geom(historical_df)
        name = nearest_sch(geom, sch_gdf)[0]
        return name

    # create dataframe containing property details to be used for prediction
    def convert_to_df(self, main_df_col, historical_postal_code_area, area_centroids, sch_gdf, train_gdf, police_centre_gdf, avg_cases_by_npc): # parse in list of training df col because predict df needs to be in same order
        # Create dataframe for property for prediction
        df = pd.DataFrame(columns=main_df_col, index=range(1))
        df['Area (SQM)'] = self.floor_area / 10.7639 #converting SQFT from input to SQM
        df['Floor Number'] = self.floor_num
        df['PPI'] = 153.3 #2020 Q4 PPI
        df['Average Cases Per Year'] = self.get_centre_avg_cases(police_centre_gdf, avg_cases_by_npc, historical_postal_code_area)
        df['Nearest Primary School'] = self.sch_dist(sch_gdf, historical_postal_code_area)
        df['nearest_station_distance'] = self.train_dist(train_gdf, historical_postal_code_area)
        df['Remaining Lease'] = self.remaining_lease

        # if the column(s) is not the base dummy column that got dropped
        if self.get_planning_area(historical_postal_code_area, area_centroids) in main_df_col:
            df[self.get_planning_area(historical_postal_code_area, area_centroids)] = 1
        if self.property_type in main_df_col:
            df[self.property_type] = 1
        # property can have more than 1 line within 1km radius
        lines = self.train_lines(train_gdf, historical_postal_code_area)
        for i in lines:
            if i in main_df_col:
                df[i] = 1

        # for remaining one-hot encoded columns that are Nan, replace with 0
        df = df.fillna(0)
        return df

    def pred_psm(self, path, main_df_col, historical_postal_code_area, area_centroids, sch_gdf, train_gdf, police_centre_gdf, avg_cases_by_npc):
        
        
        '''
        :param path: takes in path where model weights and scalers are stored
        :param main_df_col: list of training dataset column names so that prediction df tallies
        :param historical_postal_code_area: to get planning area/region of postal code if it is in our dataset instead of using distance measures due to differences in areas returned for some postal codes
        :param area_centroids: to get the planning area property is in
        :param sch_gdf: to get nearest school distance
        :param train_gdf: to get nearest stations/lines
        :param police_centre_gdf: to get nearest police centre
        :param avg_cases_by_npc: to get avg crime cases per year for nearest police centre
        :return: predicted price per sqm
        '''
        property_df = self.convert_to_df(main_df_col, historical_postal_code_area, area_centroids, sch_gdf, train_gdf, police_centre_gdf, avg_cases_by_npc)
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
        
        # Initialize model 
        model = XGBRegressor()

        # Load model
        model.load_model(path + 'model_xgboost.bin')

        # Use the loaded model to make predictions
        prediction = model.predict(property_df_scaled)[0]
        
        # Covert prediction in SQM to SQFT
        prediction = prediction / 10.7639
        return prediction


    def pred_price(self, path, main_df_col, historical_postal_code_area, area_centroids, sch_gdf, train_gdf, police_centre_gdf, avg_cases_by_npc):
        '''
        :param path: takes in path where model weights and scalers are stored
        :param main_df_col: list of training dataset column names so that prediction df tallies
        :param historical_postal_code_area: to get planning area/region of postal code if it is in our dataset instead of using distance measures due to differences in areas returned for some postal codes
        :param area_centroids: to get the planning area property is in
        :param sch_gdf: to get nearest school distance
        :param train_gdf: to get nearest stations/lines
        :param police_centre_gdf: to get nearest police centre
        :param avg_cases_by_npc: to get avg crime cases per year for nearest police centre
        :return: predicted price of unit and predicted price per sqm
        '''
        predicted_psm = self.pred_psm(path, main_df_col, historical_postal_code_area, area_centroids, sch_gdf, train_gdf, police_centre_gdf, avg_cases_by_npc)
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
prelim_ds = pd.read_csv('datasets/preliminary_dataset.csv')
postal_code_area = pd.read_csv('datasets/historical_postal_code_area.csv')
cols = list(modelling.columns)
cols.remove('Unit Price ($ PSM)')
#print(cols)
print(property.get_lat(postal_code_area))
print(property.get_lon(postal_code_area))
print(property.get_geom(postal_code_area))
print(property.get_road_name())
print(property.get_planning_area(postal_code_area, area_df))
print(property.get_planning_region(postal_code_area, area_df))
print(property.train_lines(train, postal_code_area))
print(property.train_dist(train, postal_code_area))
print(property.train_stations(train, postal_code_area))
print(property.sch_dist(sch, postal_code_area))
print(property.sch_name(sch, postal_code_area))
print(property.get_police_centre(police_centre, postal_code_area))
print(property.police_centre_dist(police_centre, postal_code_area))
print(property.get_centre_avg_cases(police_centre, avg_cases, postal_code_area))
print(property.convert_to_df(cols, postal_code_area, area_df, sch, train, police_centre, avg_cases))
print(property.pred_price('modelling/', cols, postal_code_area, area_df, sch, train, police_centre, avg_cases))
'''
