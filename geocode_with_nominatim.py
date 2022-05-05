import time
import requests
import pandas as pd
import geopandas as gpd
from pathlib import Path
from tqdm import tqdm

def geocode_fn(row, server='https://nominatim.openstreetmap.org/'):
    params = {'q': row['q'], 'limit': 1, 'format': 'json', 'bounded': 1,
              'viewbox':','.join([str(val) for val in row[['minx', 'miny', 'maxx', 'maxy']]])}
    response = requests.get(server+'/search', params=params)
    data = response.json()
    if server == 'https://nominatim.openstreetmap.org/':
        time.sleep(1) # Usage limits
    return data

if __name__ == "__main__":
    
    # Save DataFrame as csv
    df_total = pd.read_csv('outputs/df_not_geocoded_final.csv')


    df_total['nombre_q'] = df_total['q']
    df_total['q'] = df_total['address_q'].str.lower()
    
    
    batch_size = 500
    for ix in range(batch_size, df_total.shape[0], batch_size):
        df = df_total.iloc[ix:ix+batch_size]

        if Path(f'geocoded_df_missings_final_batch_{ix}.csv').exists():
            geocoded_df = pd.read_csv(f'outputs/geocoded_df_missings_final_batch_{ix}.csv', index_col=0)
        else:
            tqdm.pandas()
            geocoded = df.progress_apply(geocode_fn, axis=1)
            geocoded_exploded = geocoded.explode() # unpack lists
            geocoded_df = pd.json_normalize(geocoded_exploded) # Series of dicts -> DataFrame
            geocoded_df.to_csv(f'outputs/geocoded_df_missings_final_batch_{ix}.csv')

        # NaNs
        print(f"""
Geocoded observations: {geocoded_df['lat'].isna().value_counts().loc[False]} / {geocoded_df.shape[0]} ({(geocoded_df['lat'].isna().value_counts(normalize=True) * 100).round(2).loc[False]}%)

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

        if Path(f'outputs/geocoded_df_missings_final_batch_{ix}.geojson').exists():
            geocoded_gdf = gpd.read_file(f'outputs/geocoded_df_missings_final_batch_{ix}.geojson')
        else:
            geocoded_gdf = gpd.GeoDataFrame(
                data=geocoded_df,
                geometry=gpd.points_from_xy(geocoded_df['lon'], geocoded_df['lat']),
                crs='EPSG:4326'
            )
            geocoded_gdf = geocoded_gdf.drop('boundingbox', axis=1) # Can't save list type in geojson format
            geocoded_gdf.to_file(f'outputs/geocoded_df_missings_final_batch_{ix}.geojson', driver='GeoJSON')

