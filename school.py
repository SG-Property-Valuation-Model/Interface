'''
To get the distance to the nearest school within 2km radius of the property
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
    #print('tree: ', tree)
    #print('src points: ', src_points)
    # Returns number of schools within radius
    # Get distance of nearest school
    #print(tree.query(src_points, k=1))
    dist, ind = tree.query(src_points, k=1)

    dist = dist * 6371000
    # Count schools within radius
    count = tree.query_radius(src_points, r=rad, count_only=True)
    return count, dist.ravel()

    # Return the number of schools within the distance for each apartment wrt sale date


def nearest_sch(property_geom, sch_gdf, dist):
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

    count, nearest_dist = zip(*results)
    #count = np.concatenate(count, axis=0)
    #nearest_dist = np.concatenate(nearest_dist, axis=0)
    nearest_dist = nearest_dist[0][0]
    return nearest_dist

'''
#Testing
os.chdir('C:/Users/User/Desktop/NOTES/Notes_Y4S2/BT4222/HDB Project/Final Merge of Data/')
get_geom = gp.points_from_xy([103.80011435155], [1.44267961678131]) # function get_geom in listing
df = pd.DataFrame(data = {'geometry':get_geom})
#df = pd.DataFrame(data=d)
pri_sch = pd.read_csv('primary_sch_gdf.csv')
print(nearest_sch(get_geom, pri_sch, 2000))
'''
