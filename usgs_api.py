import datetime as dt 
import requests
import pandas as pd
from pandas import json_normalize

latitude = 18.210445
longitude = -66.487722

#today's date
today = dt.date.today().strftime("%Y-%m-%d")
min_date = dt.datetime(2019,12,25)

#set up bounding box or usgs api (bounding box is the defining space in which data will be retrieved)
rectangle = "&minlatitude=17.9465534538&minlongitude=-67.2424275377&maxlatitude=18.5206011011&maxlongitude=-65.5910037909"
url = r'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude=2&orderby=time&starttime=2019-12-28&endtime='+ today +rectangle

#request data from url and parse to json
req = requests.get(url)
data = req.json()

#get earthquakes that occured in puertorico
pr_earth = [datum for datum in data['features'] if "Puerto Rico" in datum['properties']['place']]

##normalize json to readable dataframe
df_earth = json_normalize(pr_earth,record_prefix =False,meta_prefix =False)

#remove prefix from column names and update df_earth
rename = [i.replace('properties.','') for i in df_earth.columns]
cols = list(df_earth.columns)
newCols = dict(zip(cols,rename))
df_earth.rename(columns=newCols,inplace =True)

long_lat = pd.DataFrame(df_earth['geometry.coordinates'].values.tolist(),index =df_earth.index )
df_earth[['long','lat']] = long_lat[[0,1]]
df_earth = df_earth[['time','magType','url','mag','place','long','lat']]

###convert time from miliseconds to datetime
df_earth['time'] = df_earth['time'].apply(lambda ms:pd.Timestamp(ms, unit ='ms'))

###remove "Puerto Rico" from cells in columns "place"
df_earth['place'] = df_earth['place'].apply(lambda place:place.replace(", Puerto Rico",""))