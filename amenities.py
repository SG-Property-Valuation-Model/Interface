'''
To get info (name, distance) of the nearest school within 2km radius (can change distance) of the property
To get info (name, distance) of the nearest police centre within 10km radius (can change distance) of the property
To get info (train station name(s), nearest train station distance, train line(s)) of trains within 1km radius (can change distance) of the property
'''
import pandas as pd
import numpy as np
import datetime as datetime
from sklearn.neighbors import BallTree
import geopandas as gp
from shapely import wkt
import os
import warnings
warnings.filterwarnings("ignore")

def count_amenity(src_points, candidates, rad):
    """Find amenity being searched within the stated radius
    amenity: school, train station, police centre
    """
    # Create tree from the candidate points
    tree = BallTree(candidates, leaf_size=15, metric='haversine')

    # Get distance and index of nearest amenity
    dist, nearest_ind = tree.query(src_points, k=1)

    dist = dist * 6371000
    # Count number of amenity within radius
    count = tree.query_radius(src_points, r=rad, count_only=True)
    # Get indexes of all the amenity within radius
    all_ind = tree.query_radius(src_points, r=rad)

    return count, dist.ravel(), nearest_ind, all_ind

    # Return the number of schools within the distance for each apartment wrt sale date


def nearest_sch(property_geom, sch_gdf, dist=2000): # default distance is 2km
    property_copy = pd.DataFrame(data = {'geometry':property_geom})

    sch_copy = sch_gdf.copy().reset_index(drop=True)
    sch_copy['geometry'] = sch_copy['geometry'].apply(wkt.loads)
    sch_copy = gp.GeoDataFrame(sch_copy, geometry='geometry')
    earth_radius = 6371000  # meters
    radius = dist / earth_radius

    property_geom_col = property_copy.geometry.name
    sch_geom_col = sch_copy.geometry.name

    property_copy['radians'] = property_copy[property_geom_col].apply(
        lambda geom: [geom.y * np.pi / 180, geom.x * np.pi / 180])
    sch_copy['radians'] = sch_copy[sch_geom_col].apply(lambda geom: [geom.y * np.pi / 180, geom.x * np.pi / 180])

    # Take school's opening date & closed date to be one year in advanced - forward looking
    sch_copy['adv_open_date'] = pd.to_datetime(sch_copy['opening_date']).dt.date - pd.DateOffset(years=1)
    sch_copy['adv_close_date'] = pd.to_datetime(sch_copy['closed_date']).dt.date - pd.DateOffset(years=1)
    property_copy['Sale Date'] = pd.datetime.now()

    results = property_copy.apply(lambda x: count_amenity([x['radians']], np.stack(
        sch_copy[(sch_copy['adv_open_date'] <= x['Sale Date']) & (sch_copy['adv_close_date'] >= x['Sale Date'])][
            'radians']), radius), axis=1)

    count, nearest_dist, nearest_index, all_index = zip(*results)

    index = nearest_index[0][0]
    # get distance to the nearest school
    nearest_dist = nearest_dist[0][0]
    # only if need to get nearest school's name
    nearest_pri_sch =  str(sch_copy.loc[index].Name.values[0])
    return nearest_pri_sch, nearest_dist

def nearest_police_centre(property_geom, police_centre, dist = 10000):
    property_copy = pd.DataFrame(data = {'geometry':property_geom})
    police_copy = police_centre.copy().reset_index(drop=True)
    police_copy['geometry'] = police_copy['geometry'].apply(wkt.loads)
    police_copy = gp.GeoDataFrame(police_copy, geometry='geometry')
    earth_radius = 6371000  # meters
    radius = dist / earth_radius

    property_geom_col = property_copy.geometry.name
    police_copy_geom_col = police_copy.geometry.name

    property_copy['radians'] = property_copy[property_geom_col].apply(
        lambda geom: [geom.y * np.pi / 180, geom.x * np.pi / 180])
    police_copy['radians'] = police_copy[police_copy_geom_col].apply(lambda geom: [geom.y * np.pi / 180, geom.x * np.pi / 180])
    results = property_copy.apply(lambda x: count_amenity([x['radians']], np.stack(police_copy['radians']), radius), axis=1)

    count, nearest_dist, nearest_index, all_index = zip(*results)
    index = nearest_index[0][0]
    nearest_centre = str(police_copy.iloc[index]['Police Centre'].values[0]).replace(u'\xa0', u'')

    return nearest_dist, nearest_centre

def nearest_train(property_geom, train_gdf, dist = 1000):
    property_copy = pd.DataFrame(data={'geometry': property_geom})
    train_gdf_copy = train_gdf.copy().reset_index(drop=True)
    train_gdf_copy['geometry'] = train_gdf_copy['geometry'].apply(wkt.loads)
    earth_radius = 6371000  # meters
    radius = dist / earth_radius

    property_geom_col = property_copy.geometry.name
    train_gdf_copy_geom_col = train_gdf_copy.geometry.name

    property_copy['radians'] = property_copy[property_geom_col].apply(
        lambda geom: [geom.y * np.pi / 180, geom.x * np.pi / 180])
    train_gdf_copy['radians'] = train_gdf_copy[train_gdf_copy_geom_col].apply(lambda geom: [geom.y * np.pi / 180, geom.x * np.pi / 180])
    results = property_copy.apply(lambda x: count_amenity([x['radians']], np.stack(train_gdf_copy['radians']), radius), axis=1)
    count, nearest_dist, nearest_index, all_index = zip(*results)

    index = nearest_index[0][0]
    all_index = np.hstack(all_index).squeeze().tolist()
    # all lines within radius
    lines = set(train_gdf_copy.iloc[all_index]['COLOR'].values)
    # all stations within radius
    stations = set(train_gdf_copy.iloc[all_index]['STN_NAME'].values)
    nearest_dist = nearest_dist[0][0]

    return nearest_dist, lines, stations

'''
#Testing
path = 'datasets/'
get_geom = gp.points_from_xy([103.878360066595], [1.37415222602816]) # function get_geom in listing
df = pd.DataFrame(data = {'geometry':get_geom})
#df = pd.DataFrame(data=d)
pri_sch = pd.read_csv(path + 'primary_sch_gdf.csv')
print(nearest_sch(get_geom, pri_sch))
police = pd.read_csv(path + 'police_centre_gdf.csv')
print(nearest_police_centre(get_geom, police))
train = pd.read_csv(path + 'train_gdf.csv')
print(nearest_train(get_geom, train)[0])
print(nearest_train(get_geom, train)[1])
print(nearest_train(get_geom, train)[2])
'''