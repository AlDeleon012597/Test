import os
from pathlib import Path
import pandas as pd 

parent_dir = Path(__file__).resolve().parent

###create csv paths
counties_2018_SVI_path = os.path.join(parent_dir,'CSV','counties_SVI.csv')
tracts_2018_SVI_path =  os.path.join(parent_dir,'CSV','tracts_SVI.csv')

###Read csvs
counties_SVI = pd.read_csv(counties_2018_SVI_path,encoding = 'ISO-8859-1')
tracts_SVI = pd.read_csv(tracts_2018_SVI_path,encoding = 'ISO-8859-1')

##geojsons for chloropleth map
county_geojson =  os.path.join(parent_dir,'geojsons','County.geojson')
tracts_geojson =  os.path.join(parent_dir,'geojsons','Tracts1.geojson')