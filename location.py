'''
To get longitude, latitude, building name, planning area and planning region of property based on postal code
'''
import pandas as pd
import numpy as np
import json, math, os, re, requests, time
import geopandas as gp
from shapely import wkt
from sklearn.neighbors import BallTree

# Using requests to call geographic information from OneMap API
def get_info(searchVal, returnGeom=True, getAddr=True, pageNum=1):
    if returnGeom:
        returnGeom = 'Y'
    else:
        returnGeom = 'N'

    if getAddr:
        getAddr = 'Y'
    else:
        getAddr = 'N'

    url = 'https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom={}&getAddrDetails={}&pageNum={}'
    url = url.format(searchVal, returnGeom, getAddr, pageNum)
    #print(url)
    return json.loads(requests.get(url).content.decode("UTF-8"))['results']
    
# Get (long, lat, building name) for unique postal codes only to reduce runtime
def postal_search(postal_code):
    response = get_info(searchVal=postal_code)[0]
    lon = response['LONGITUDE']
    lat = response['LATITUDE']
    building = response['BUILDING']
    road_name = response['ROAD_NAME']
    return lon, lat, building, road_name

def area_region(postal_code, area_centroids):
    lon, lat, building, road_name = postal_search(postal_code)
    geometry = gp.points_from_xy([lon], [lat])
    property_radians = np.ravel([geometry.y * np.pi / 180, geometry.x * np.pi / 180])
    area_centroids_copy = area_centroids.copy()
    right_geom_col = area_centroids.geometry.name

    area_centroids_copy[right_geom_col] = area_centroids[right_geom_col].apply(wkt.loads)
    area_centroids_copy = gp.GeoDataFrame(area_centroids_copy, geometry=right_geom_col)

    right_radians = np.array(
        area_centroids_copy[right_geom_col].apply(lambda geom: (geom.y * np.pi / 180, geom.x * np.pi / 180)).to_list())

    tree = BallTree(right_radians, leaf_size=15, metric='haversine')

    # Find closest planning area
    dist, ind = tree.query([property_radians], k=1)
    indices = ind.transpose()
    closest = indices[0]
    closest_area = area_centroids_copy.iloc[closest]['Planning Area'].values[0]
    region = area_centroids_copy.iloc[closest]['Planning_Region'].values[0]
    return closest_area, region

'''
# Testing
df = pd.read_csv('datasets/preliminary_dataset.csv')
area = pd.read_csv('datasets/area_centroid.csv')
print(postal_search('098656'))
print(area_region('098656', area))
'''