import time
import requests
import pandas as pd
import geopandas as gpd
from pathlib import Path
from tqdm import tqdm

def geocode_fny(row, server='https://nominatim.openstreetmap.org/'):
    params = {'q': row['q'], 'limit': 1, 'format': 'json', 'bounded': 1,
              'viewbox':','.join([str(val) for val in row[['minx', 'miny', 'maxx', 'maxy']]])}
    response = requests.get(server+'/search', params=params)
    data = response.json()
    if server == 'https://nominatim.openstreetmap.org/':
        time.sleep(1) # Usage limits
    return data

if __name__ == "__main__":
    
    # Save DataFrame as csv
    df_not_geocoded_final = pd.read_csv('outputs/df_not_geocoded_final.csv')


    df_not_geocoded_final['nombre_q'] = df_not_geocoded_final['q']
    df_not_geocoded_final['q'] = df_not_geocoded_final['address_q'].str.lower()

    if Path('geocoded_df_missings_final.csv').exists():
        geocoded_df = pd.read_csv('outputs/geocoded_df_missings_final.csv', index_col=0)
    else:
        tqdm.pandas()
        geocoded = df.progress_apply(geocode_fn, axis=1)
        geocoded_exploded = geocoded.explode() # unpack lists
        geocoded_df = pd.json_normalize(geocoded_exploded) # Series of dicts -> DataFrame
        geocoded_df.to_csv('outputs/geocoded_df_missings_final.csv')

    # NaNs
    print(f"""
Geocoded observations:
---------------------

Total:
-----
{geocoded_df['lat'].isna().value_counts()}

Percentage:
----------
{(geocoded_df['lat'].isna().value_counts() / geocoded_df.shape[0] * 100).round(2)}

OSM Data types:
--------------
{geocoded_df['osm_type'].value_counts()}

OSM Class:
---------
{geocoded_df['class'].value_counts()}

OSM Class type:
--------------
{geocoded_df['type'].value_counts()}
    """)

    if Path('geocoded_df_missings_final.geojson').exists():
        geocoded_gdf = gpd.read_file('geocoded_df_missings_final.geojson')
    else:
        geocoded_gdf = gpd.GeoDataFrame(
            data=geocoded_df,
            geometry=gpd.points_from_xy(geocoded_df['lon'], geocoded_df['lat']),
            crs='EPSG:4326'
        )
        geocoded_gdf = geocoded_gdf.drop('boundingbox', axis=1) # Can't save list type in geojson format
        geocoded_gdf.to_file('geocoded_df_missings_final.geojson', driver='GeoJSON')

