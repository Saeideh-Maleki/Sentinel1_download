#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import ee
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
import re
import geemap  

########## Code to download S1 data (VV and VH polarizations, and incidence angle) as csv for both ascending and descning orbits.

ee.Initialize()

def get_s1_grd(aoi, start_date, end_date, orbit_pass):
    s1_col = (ee.ImageCollection('COPERNICUS/S1_GRD')
              .filterBounds(aoi)
              .filterDate(start_date, end_date)
              .filter(ee.Filter.eq('instrumentMode', 'IW'))
              .filter(ee.Filter.eq('orbitProperties_pass', orbit_pass)))
    return s1_col

def get_polarizations(image):
    vv = image.select('VV').rename('VV')
    vh = image.select('VH').rename('VH')
    angle = image.select('angle').rename('incidence_angle')
    return {'VV': vv, 'VH': vh, 'incidence_angle': angle}


startday = '2020-04-01'
endday = '2020-09-30'
extent_gee = ' The path to a geographic region  in Google Earth Engine (GEE). It is used to define the area of interest (AOI) when selecting Sentinel-1 data.'
path_GEE = 'The path to shapefile in GEE contains the polygons you are intrested to have S1 value for each one'
shapefile_path = 'The local path  to the shapefile contains the polygons you are intreseted to have S1 value for each one.'
raw_output_path = 'The output path'

shapefile = gpd.read_file(shapefile_path)
listd = pd.date_range(startday, endday, freq='3D').strftime("%Y-%m-%d").tolist()

roi = ee.FeatureCollection(extent_gee)
plots = ee.FeatureCollection(path_GEE)

def simplify_feature(feature):
    geometry = feature.geometry()
    simplified_geometry = geometry.simplify(maxError=10)
    return feature.setGeometry(simplified_geometry)

simplified_features = plots.map(simplify_feature)

count = 100
collectionSize = len(shapefile)
chunk = 10000

# Iterate over each date range
for iii in tqdm(range(len(listd) - 1)):
    try:
        print(f"Processing range {iii}: {listd[iii]} to {listd[iii + 1]}")
        START_DATE = listd[iii]
        END_DATE = listd[iii + 1]
        
        for orbit_pass in ['ASCENDING', 'DESCENDING']:
            s1_col = get_s1_grd(roi, START_DATE, END_DATE, orbit_pass)
            
            num_images = s1_col.size().getInfo()
            if num_images == 0:
                print(f"No images found for {orbit_pass} orbit between {START_DATE} and {END_DATE}")
                continue
            else:
                print(f"Found {num_images} images for {orbit_pass} orbit between {START_DATE} and {END_DATE}")

            for idx in range(min(count, num_images)):
                try:
                    img = ee.Image(s1_col.toList(1, idx).get(0))
                    polarizations = get_polarizations(img)
                    
                    orbit_number = img.get('system:orbitNumber').getInfo()
                    name = str(img.getInfo()['properties']['system:index'])
                    orbit = str(img.getInfo()['properties']['relativeOrbitNumber_stop'])
                    m = re.search(r'(\d{8}T\d{6})', name)
                    img_name = f"{m.groups(0)[0]}_ORBIT_{orbit}"

                    df_all = []
                    subset_idx = 0

                    while subset_idx <= collectionSize:
                        subset = ee.FeatureCollection(simplified_features.toList(chunk, subset_idx))
                        subset_idx += chunk

                        for band_name, band_img in polarizations.items():
                            full_img_name = f"{img_name}_{band_name}_{orbit_pass}_{orbit_number}_{subset_idx}"
                            meanDictionary = band_img.reduceRegions(**{
                                'collection': subset,
                                'reducer': ee.Reducer.mean(),
                                'scale': 10
                            })

                            # Export the results to Google Drive
                          #  task = ee.batch.Export.table.toDrive(
                          #      collection=meanDictionary,
                          #      description=full_img_name,
                          #      fileNamePrefix=full_img_name,
                          #      fileFormat='CSV',
                          #      folder='S1n'
                          #  )
                          #  task.start()  # Start the task
                            
                            # Export the results to your local drive
                            df1 = geemap.ee_to_csv(meanDictionary, raw_output_path + f'/{img_name}.csv')
                            df_all.append(meanDictionary)
                except Exception as e:
                    print(f"Error processing image {idx} in {orbit_pass} orbit for range {iii}: {e}")
                    break

    except Exception as e:
        print(f"Error processing range {iii}: {e}")

