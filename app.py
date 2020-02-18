import json
import pandas as pd
import plotly
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import dash_table
import datetime as dt
from pandas.io.json import json_normalize
import requests
import numpy as np
from pathlib import Path
import os

parent_dir = Path(__file__).resolve().parent

countys_csv_path = os.path.join(parent_dir,r'CSV\Municipio_SVI_2018_0.csv')
tracts_csv_path =  os.path.join(parent_dir,r'CSV\Tracts_SVI_2018_0.csv')

countys_csv = pd.read_csv(countys_csv_path,encoding = 'ISO-8859-1',sep = '\t')
tracts_csv = pd.read_csv(tracts_csv_path,encoding = 'ISO-8859-1',sep = '\t')

##geojsons for chloropleth map
county_geojson =  os.path.join(parent_dir,r'geojsons\Municipio_SVI_2018.geojson')
tracts_geojson =  os.path.join(parent_dir,r'geojsons\Tracts_SVI_2018.geojson')

##mapbox token needed to display pr basemap
mapbox_accesstoken = 'pk.eyJ1IjoiYWxleGRlbGVvbjEyMyIsImEiOiJjazV1ZWRyanAwYzc2M2pucHVjejdrd2RhIn0.Z1O79Tq170L5eAzyKa-1jQ'

##Colors for bar graph and chloropleth map
pl_deep=[[0.0, 'rgb(253, 253, 204)'],
         [0.1, 'rgb(201, 235, 177)'],
         [0.2, 'rgb(145, 216, 163)'],
         [0.3, 'rgb(102, 194, 163)'],
         [0.4, 'rgb(81, 168, 162)'],
         [0.5, 'rgb(72, 141, 157)'],
         [0.6, 'rgb(64, 117, 152)'],
         [0.7, 'rgb(61, 90, 146)'],
         [0.8, 'rgb(65, 64, 123)'],
         [0.9, 'rgb(55, 44, 80)'],
         [1.0, 'rgb(39, 26, 44)']]

### SVI Themes 
themes = {'Household Composition and Disability':'HSECOMP', 
          'Minority Status and Language':'MINLANG', 
          'Housing and Transportiation':'HSETRANS', 
          'Socioeconomic Status':'SOCIOECON',
          'Overall Rank':'OVERALL'}  
		  

# Center of Puerto Rico:latitude and longitude values
latitude = 18.210445
longitude = -66.487722

#today's date
today = dt.date.today().strftime("%Y-%m-%d")

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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

###set up general layout for application
app.layout = html.Div(children=[
    html.Img(className="logo", src=app.get_asset_url("Centro_Logo.png")),
    html.H1(id = "title", children='Hazard Vulnerability'),
    #dcc.Tabs(id = ')
    html.Div([
        html.Div([
            dcc.Tabs(id="tabs-example", value='tab-1', children=[
                dcc.Tab(
                        label='About',
                        value='tab-1',
                        children = [
                                    html.H1("About page")
                                ],
                            ),
                dcc.Tab(
                        label='Options',
                        value='tab-2',
                        children = [
                                    html.P(
                                        "Filter by SVI Theme:",
                                        className = "control_label"
                                        ),
                                    dcc.Dropdown(
                                        id='theme',
                                        options=[{'label': theme, 'value': themes[theme]} for theme in themes],
                                        value='OVERALL',
                                        className = "filter_control"
                                        ),
                                    html.P(
                                        "Filter by Geography:",
                                        className = "control_label"
                                        ),
                                    dcc.RadioItems(
                                        id='geo',
                                        options=[{'label': i, 'value': i} for i in ['Tracts', 'County']],
                                        value='Tracts',
                                        labelStyle={'display': 'inline-block'},
                                        className = "filter_control"
                                        ),
                                    html.P(
                                        "Specify Earthquake magnitude:",
                                        className = "control_label "
                                        ),
                                    dcc.Input(
                                        id="_min",
                                        type="number",
                                        debounce=True,
                                        placeholder="Min",
                                        min = 3,
                                        max = 5,
                                        step = .1,
                                        className = "filter_control"
                                        ),
                                    dcc.Input(
                                        id="_max",
                                        type="number",
                                        placeholder="Max",
                                        min=5,
                                        max=10,
                                        step = .1,
                                        className = "filter_control"
                                        ),
                                     html.P(
                                        "Layers:",
                                        className = "control_label "
                                        ),
                                    dcc.Checklist(
                                        id = 'layers',
                                        options=[
                                            {'label': 'SVI Chloropleth', 'value': 'SVI'},
                                            {'label': 'Earthquakes', 'value': 'EQ'},
                                        ],
                                        value=['SVI', 'EQ'],
                                        labelStyle={'display': 'inline-block'},
                                        className = "filter_control "
                                        )
                                    ],
                                ),
                        dcc.Tab(
                            label='Data',
                            value='tab-3',
                            children = [                                  
                                        dcc.Upload(
                                            id="upload-data",
                                            children=html.Div(
                                                [
                                                    "Drag and Drop or "
                                                    "click to import "
                                                    ".CSV file here!"
                                                ],
                                            style={
                                                'width': '95%',
                                                'height': '60px',
                                                'lineHeight': '60px',
                                                'borderWidth': '1px',
                                                'borderStyle': 'dashed',
                                                'borderRadius': '5px',
                                                'textAlign': 'center',
                                                'margin': '10px'
                                            },
                                            ),
                                            multiple=True,
                                        ),
                                    ],
                                ),
                            ],
                        className = "content"
                        ),
                    ],
                className = "one container_one"
            ),
        html.Div(
            [
            html.Div(
                [
                dash_table.DataTable(
                    id='datatable-interactivity',
                    columns=[
                        {'name': i, 'id': i, 'deletable': True} for i in df_earth.columns
                        # omit the id column
                        if i != 'id'
                    ],
                    data=df_earth.to_dict('records'),
                    editable=False,
                    sort_action="native",
                    sort_mode='multi',
                    row_selectable='multi',
                    row_deletable=True,
                    selected_rows=[],
                    page_action='native',
                    page_current= 0,
                    page_size= 10,
                    style_table = {"width":"auto"},
                    ),
                ],
            className = "container_one"
            ),
        ],
    className = "two"
    ),
        html.Div(
            [
            dcc.Graph(
                id='pr-chloro',
                className = "container_one"
                )
            ], 
        className = "three"
        ),
        html.Div(
            [
            dcc.Graph(
                id='pr-bar',
                className = "container_one",
                loading_state = {"is_loading":True}
                ),
            ],  
        className = " four"
        ),
    ],
             className = "container-display"),
##    dcc.Graph(
##        id='usgs-scatter'
##        ),
    html.Div(children='''
        Data source from CDC @Jan 2020
    ''')
   ])

colormap = {(2.0,3.0):{"size":4,"color":"#fee5d9"},
            (3.0,3.5):{"size":7,"color":"#fcae91"},
            (4.0,4.5):{"size":11,"color":"#fb6a4a"},
            (4.5,5):{"size":15,"color":"#de2d26"},
            (5.0,10):{"size":20,"color":"#a50f15"}}

        
##switches geojson property id to geoid
def parsegeojson(geo):
    with open(geo) as f:
        pr_data = json.load(f)
        for feature in pr_data['features']:
            geoid = feature["properties"]['GEOID']
            feature['id'] = geoid
    return pr_data

##ranks and sorts themes for barchart
def rankThemes(df_themes,theme):
    themerank = theme + "_rank"
    df_themes[themerank] = df_themes[theme].rank(ascending=False)
    x = df_themes.sort_values([themerank])["NAME"].tolist()
    y = df_themes.sort_values([themerank])[theme].tolist()
    return x,y

###assigns attributes based on user-selection
def setAttr(geo,theme, bar = bool):
    if geo == 'County':
        geo = county_geojson
        df = countys_csv
        text = df['NAME'].str.title().tolist()
        x,y = rankThemes(df,theme)

    if geo == 'Tracts':
        geo = tracts_geojson
        df = tracts_csv
        text = df['Tract_Name'].str.title().tolist()
        avg_themes = df.groupby(['NAME'],as_index=False)['HSECOMP','MINLANG','HSETRANS','SOCIOECON','OVERALL'].mean()
        
        theme_max = avg_themes[theme].max()
        theme_min = avg_themes[theme].min()
        avg_themes[theme] = avg_themes[theme].apply(lambda x:(x-theme_min)/(theme_max-theme_min)) ###Normalizes averages to a scale of 0-1
        x,y =rankThemes(avg_themes,theme)
    
    if bar:
        return geo,df,text,x,y
    else:
        return geo,df,text


def setmag(_min,_max): 
    if _min and not _max:
        df_magrange = df_earth.loc[ _min < df_earth['mag']]
    elif not _min and _max:
        df_magrange = df_earth.loc[df_earth['mag'] < _max]
    elif _max and _min:
        df_magrange = df_earth.loc[ (_min < df_earth['mag']) & (df_earth['mag'] < _max)]
    else:
        df_magrange = df_earth     
    return df_magrange
    
    
@app.callback(
    Output('pr-chloro', 'figure'),
    [Input('theme', 'value'),
     Input('geo', 'value'),
     Input('_min', 'value'),
     Input('_max', 'value'),
     Input('layers','value')
     ])

def update_chloro(theme, geo,_min,_max, layers):
    traces = []   
    if "EQ" in layers:
        df_mags = setmag(_min,_max)
        for mag_range in colormap:
            if mag_range == (5.0,10):
                name = "{} {}".format(mag_range[0],"and up")
            else:   
                name = "{0} to {1}".format(mag_range[0],mag_range[1])
            df_mags_range = df_mags.loc[(df_mags['mag'] >= mag_range[0]) & (df_mags['mag']<mag_range[1])]
            traces.append(go.Scattermapbox(
                lat=df_mags_range['lat'],
                lon=df_mags_range['long'],
                mode='markers',
                marker={"color":colormap[mag_range]['color'],
                            "size":colormap[mag_range]['size'],
                            "opacity": 1},   
                name = "{0} to {1}".format(mag_range[0],mag_range[1]),            
                text= df_mags_range[['place','mag']],
                texttemplate = "%Name:%{df_mags_range['place']}\nMagnitude:%{df_mags_range['mag']}",
                showlegend = True

            ))
    if "SVI" in layers:
        geo,df_chloro,text = setAttr(geo,theme, bar=False)
        pr_data = parsegeojson(geo)
        traces.append(go.Choroplethmapbox(
            geojson = pr_data,
            locations = df_chloro['GEOID'].tolist(),
            z = df_chloro[theme].tolist(), 
            colorscale = pl_deep,
            text = text, 
            colorbar = dict(thickness=20, ticklen=3),
            marker_line_width=0, 
            marker_opacity=0.6,
            subplot='mapbox1')
            ),
            
    layout = go.Layout(
        clickmode="event+select",
        autosize = True,
        #automargin = True,
        mapbox1 = dict(
            domain = {'x': [0, 1],'y': [0, 1]},
            center = dict(lat=latitude, lon=longitude),
            accesstoken = mapbox_accesstoken, 
            zoom = 7.5,
            style ='carto-positron'
            ),
        margin=dict(l=10, r=50, t=10, b=20)
        #padding=dict(left=10,r=10,t=10,b=10),
        #paper_bgcolor='rgb(204, 204, 204)',
        #plot_bgcolor='rgb(204, 204, 204)',
    )
    
    return {"data":traces,"layout":layout}

@app.callback(
    Output('pr-bar', 'figure'),
    [Input('theme', 'value'),
     Input('geo', 'value')])

def update_bar(theme, geo):
    geo,df,text,x,y = setAttr(geo,theme,bar=True)
    
    traces = go.Bar(
        y=y,
        x=x,
        xaxis='x2',
        yaxis='y2',
        marker=dict(
            color='rgba(91, 207, 135, 0.3)',
            line=dict(
                color='rgba(91, 207, 135, 2.0)',
                width=0.3),
        ),
        orientation='v',
    )
    
    layout = go.Layout(
        autosize = True,
        xaxis2={
            'zeroline': False,
            "showline": False,
            "showticklabels":True,
            'showgrid':True,
            'domain': [0, 1],
            'side': 'left',
            'anchor': 'x2',
        },

        yaxis2={
            'domain': [0, 1],
            'range': [0,1],
            'anchor': 'y2',

        },
        margin=dict(l=100, r=75, t=50, b=110),
        #paper_bgcolor='rgb(204, 204, 204)',
        #plot_bgcolor='rgb(204, 204, 204)',
    )
    
    return {"data":[traces],"layout":layout}

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
