'''
To get the distance to the nearest school within 2km radius (can change distance) of the property
To get the distance to the nearest police centre within 10km radius (can change distance) of the property
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

def count_sch(src_points, candidates, rad):
    """Find schools within the stated radius"""
    # Create tree from the candidate points
    tree = BallTree(candidates, leaf_size=15, metric='haversine')

    # Returns number of schools within radius
    # Get distance of nearest school
    #print(tree.query(src_points, k=1))
    dist, ind = tree.query(src_points, k=1)

    dist = dist * 6371000
    # Count schools within radius
    count = tree.query_radius(src_points, r=rad, count_only=True)
    return count, dist.ravel(), ind

    # Return the number of schools within the distance for each apartment wrt sale date


def nearest_sch(property_geom, sch_gdf, dist=2000): # default distance is 2km
    property_copy = pd.DataFrame(data = {'geometry':property_geom})
    #property_copy = property.copy().reset_index(drop=True)
    #property_copy = gp.GeoDataFrame(
        #property_copy, geometry=property_copy.geometry)
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

    results = property_copy.apply(lambda x: count_sch([x['radians']], np.stack(
        sch_copy[(sch_copy['adv_open_date'] <= x['Sale Date']) & (sch_copy['adv_close_date'] >= x['Sale Date'])][
            'radians']), radius), axis=1)

    # count: only if need to get number of schools within dist
    count, nearest_dist, index = zip(*results)

    index = index[0][0]
    # get distance to the nearest school
    nearest_dist = nearest_dist[0][0]
    # only if need to get nearest school's name
    # nearest_school =  sch_copy.loc[index].Name
    return nearest_dist

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
    results = property_copy.apply(lambda x: count_sch([x['radians']], np.stack(police_copy['radians']), radius), axis=1)

    # count: only if need to get number of police centres within dist
    count, nearest_dist, index = zip(*results)
    index = index[0][0]
    nearest_centre = str(police_copy.iloc[index]['Police Centre'].values[0]).replace(u'\xa0', u'')

    return nearest_centre

'''
#Testing
path = 'datasets/'
get_geom = gp.points_from_xy([103.814673696844], [1.26681341314756]) # function get_geom in listing
df = pd.DataFrame(data = {'geometry':get_geom})
#df = pd.DataFrame(data=d)
pri_sch = pd.read_csv(path + 'primary_sch_gdf.csv')
print(nearest_sch(get_geom, pri_sch))
police = pd.read_csv(path + 'police_centre_gdf.csv')
print(nearest_police_centre(get_geom, police))
'''
