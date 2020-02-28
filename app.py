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

###create csv paths
counties_2018_SVI_path = os.path.join(parent_dir,'CSV','counties_SVI.csv')
tracts_2018_SVI_path =  os.path.join(parent_dir,'CSV','tracts_SVI.csv')

###Read csvs
counties_SVI = pd.read_csv(counties_2018_SVI_path,encoding = 'ISO-8859-1')
tracts_SVI = pd.read_csv(tracts_2018_SVI_path,encoding = 'ISO-8859-1')

##geojsons for chloropleth map
county_geojson =  os.path.join(parent_dir,'geojsons','Municipio_SVI_2018.geojson')
tracts_geojson =  os.path.join(parent_dir,'geojsons','Tracts.geojson')

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


choro_colormap = {(2.0,3.0):{"size":4,"color":"#fee5d9"},
            (3.0,3.5):{"size":7,"color":"#fcae91"},
            (4.0,4.5):{"size":11,"color":"#fb6a4a"},
            (4.5,5):{"size":15,"color":"#de2d26"},
            (5.0,10):{"size":20,"color":"#a50f15"}}

scat_colormap = {'ml':'#a6cee3',
                 'Mint': '#1f78b4',
                 'me':'#b2df8a',
                 'mwr':'#33a02c',
                 'mwb':'#fb9a99',
                 'mwc':'#e31a1c',
                 'mww':'#fdbf6f',
                 'mb':'#ff7f00',
                 'mfa':'#cab2d6',
                 'mb_lg':'#6a3d9a',
                 'md':'#b15928'}

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
todayList = today.split('-')
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
            dcc.Tabs(id="tabs-example", value='tab-2', children=[
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
                                    html.Button("Filter by SVI Theme:",
                                                id='button'),
                                    html.Div([
                                        dcc.Dropdown(
                                            id='theme',
                                            options=[{'label': theme, 'value': themes[theme]} for theme in themes],
                                            value='OVERALL',
                                            className = "filter_control"
                                            ),
                                        dcc.Dropdown(
                                            id='year',
                                            options=[{'label': year, 'value': suffix} for year,suffix in [(2016,"_16"),(2017,"_17"),(2018,"_18")]],
                                            value= "_18",
                                            className = "filter_control",
                                            ),
                                         ],
                                        style= {'display': 'block'},
                                        id = 'svi_div'
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
                                        className = "filter_control",
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
                                        className = "filter_control",
                                        ),
                                    dcc.Input(
                                        id="_max",
                                        type="number",
                                        placeholder="Max",
                                        min=5,
                                        max=10,
                                        step = .1,
                                        className = "filter_control",
                                        ),
                                    dcc.DatePickerRange(
                                            id='date-picker',
                                            className = 'filter_control',
                                            min_date_allowed=dt.datetime(2016, 8, 5),
                                            max_date_allowed=today,
                                            initial_visible_month=today,
                                            end_date=today,
                                            start_date = dt.datetime(2019,12,28),

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
                                        ),
                                    ]) ,
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
                        ),
                    ],
                className = "one container_one content"
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
                    page_size= 13,
                    style_table = {"width":"auto"},
                    ),
                ],
            className = "container_one Two"
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
        html.Div(
            [
            dcc.Graph(
                id='mag_scat',
                className = "container_one",
                ),
            ],
        className = " five"
        ),
    ],
             className = "container-display"),
   ],
)

##switches geojson property id to geoid
def parsegeojson(geo):
    with open(geo) as f:
        pr_data = json.load(f)
        for feature in pr_data['features']:
            geoid = feature["properties"]['GEOID']
            feature['id'] = geoid
    return pr_data

##ranks and sorts themes for barchart
def rankThemes(geo,theme,year):
    if geo == 'County':
       df_themes = counties_SVI

    if geo == 'Tracts':
        theme_cols = [col for col in tracts_SVI.columns if theme in col]
        tracts_clean = tracts_SVI.loc[tracts_SVI[theme_cols[0]] != -99999]
        avg_themes = tracts_clean.groupby(['MUNICIPIO'],as_index=False)[theme_cols].mean()
        theme_max = avg_themes[theme_cols].max()
        theme_min = avg_themes[theme_cols].min()

        for selectedTheme in theme_cols:
            avg_themes[selectedTheme] = avg_themes[selectedTheme].apply(lambda x:(x-theme_min[selectedTheme])/(theme_max[selectedTheme]-theme_min[selectedTheme]))

        df_themes = avg_themes

    themerank = theme + year + "_rank"
    df_themes[themerank] = df_themes[theme + year].rank(ascending=False)

    municipios = df_themes.sort_values([themerank])["MUNICIPIO"].tolist()
    theme_16 = df_themes.sort_values([themerank])[theme + "_16"].tolist()
    theme_17 = df_themes.sort_values([themerank])[theme + "_17"].tolist()
    theme_18 = df_themes.sort_values([themerank])[theme + "_18"].tolist()

    return municipios,theme_16, theme_17, theme_18

###assigns attributes based on user-selection
def setAttr(geo,theme):
    if geo == 'County':
        geo = county_geojson
        df = [counties_SVI]
        text = df[0]['MUNICIPIO'].str.title().tolist()

    if geo == 'Tracts':
        geo = tracts_geojson
        theme_cols = [col for col in tracts_SVI.columns if theme in col]

        df_clean = tracts_SVI.loc[tracts_SVI[theme_cols[0]] != -99999]
        df_na = tracts_SVI.loc[tracts_SVI[theme_cols[0]] == -99999]

        df = [df_clean,df_na]
        text = df[0]['TRACT'].str.title().tolist()

    return geo,df,text


def setRange(lower,upper,col):

    if lower and not upper:
        df_range = df_earth.loc[lower < df_earth[col] ]

    elif not lower and upper:
        df_range = df_earth.loc[df_earth[col] < upper]

    elif lower and upper:
        df_range = df_earth.loc[ (lower < df_earth[col]) & (df_earth[col] < upper)]

    else:
        df_range = df_earth
    return df_range


@app.callback(
   Output(component_id='svi_div', component_property='style'),
   [Input(component_id='button', component_property='n_clicks')])

def show_hide_element(n_clicks):
    if not n_clicks:
        return {'display': 'none'}
    elif (n_clicks % 2) == 0:
        return {'display': 'none'}
    else:
        return {'display': 'block'}

@app.callback(
    dash.dependencies.Output('mag_scat', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('_min', 'value'),
     Input('_max', 'value'),])

def updatescatterplot(start, end,_min,_max):
    df_mags = setRange(_min,_max,'mag')
    df_time = setRange(start,end,'time')
    traces = []
    for magType in scat_colormap:
        if magType in df_mags['magType'].values.tolist():
            traces.append(go.Scatter(
                y=df_mags[df_mags['magType'] == magType]['mag'],
                x=df_time['time'],
                xaxis='x2',
                yaxis='y2',
                mode="markers",
                marker_color = scat_colormap[magType],
                orientation='v',
                name = magType,
            ))

    layout = go.Layout(
        autosize = True,
        xaxis2={
            'title':'Time',
            'zeroline': False,
            "showline": False,
            "showticklabels":True,
            'showgrid':True,
            'domain': [0, 1],
            'side': 'left',
            'anchor': 'x2',
        },

        yaxis2={
            'title': 'Magnitude',
            'domain': [0, 1],
            'range': [0,10],
            'anchor': 'y2',

        },
        margin=dict(l=100, r=75, t=50, b=110))

    return {"data":traces,"layout":layout}

@app.callback(
    Output('pr-chloro', 'figure'),
    [Input('theme', 'value'),
     Input('geo', 'value'),
     Input('_min', 'value'),
     Input('_max', 'value'),
     Input('layers','value'),
     Input('year','value')
     ])

def update_chloro(theme, geo,_min,_max, layers,year):
    traces = []
    if "EQ" in layers:
        df_mags = setRange(_min,_max,'mag')
        for mag_range in choro_colormap:
            if mag_range == (5.0,10):
                name = "{} {}".format(mag_range[0],"and up")
            else:
                name = "{0} to {1}".format(mag_range[0],mag_range[1])
            df_mags_range = df_mags.loc[(df_mags['mag'] >= mag_range[0]) & (df_mags['mag']<mag_range[1])]

            traces.append(go.Scattermapbox(
                lat=df_mags_range['lat'],
                lon=df_mags_range['long'],
                mode='markers',
                marker={"color":choro_colormap[mag_range]['color'],
                            "size":choro_colormap[mag_range]['size'],
                            "opacity": 1},
                name = "{0} to {1}".format(mag_range[0],mag_range[1]),
                text= df_mags_range[['place','mag']],
                texttemplate = "%Name:%{df_mags_range['place']}\nMagnitude:%{df_mags_range['mag']}",
                showlegend = True,
            ))

    if "SVI" in layers:
        geojson,df_chloro,text = setAttr(geo,theme)
        pr_data = parsegeojson(geojson)
        traces.append(go.Choroplethmapbox(
            geojson = pr_data,
            locations = df_chloro[0]['GEOID'].tolist(),
            z = df_chloro[0][theme + year].tolist(),
            colorscale = pl_deep,
            text = text,
            colorbar = dict(thickness=20,
                            ticklen=3,
                            xanchor = 'left',
                            x= 0),
            marker_line_width=0,
            marker_opacity=0.6,
            subplot='mapbox1')
            ),

        if geo == 'Tracts':
            traces.append(go.Choroplethmapbox(
                geojson = pr_data,
                locations = df_chloro[1]['GEOID'].tolist(),
                z = df_chloro[1][theme + year].tolist(),
                text = text,
                colorbar = dict(thickness=20,
                            ticklen=3,
                            xanchor = 'left',
                            x= -1),
                autocolorscale = False,
                showscale = False,
                marker_line_width=0,
                marker_opacity=0.8,
                subplot='mapbox1')
                ),

    layout = go.Layout(
        clickmode="event+select",
        autosize = True,
        #automargin = True,
        updatemenus=[
            dict(
                buttons=(
                    [
                        dict(
                            args=[
                                {
                                    "mapbox.zoom": 7.5,
                                    "mapbox.center.lon": longitude,
                                    "mapbox.center.lat": latitude,
                                    "mapbox.bearing": 0,
                                    "mapbox.style": "dark",
                                }
                            ],
                            label="Reset Zoom",
                            method="relayout",
                        )
                    ]
                ),
                direction="left",
                pad={"r": 0, "t": 0, "b": 0, "l": 0},
                showactive=False,
                type="buttons",
                x=0.45,
                y=0.02,
                xanchor="left",
                yanchor="bottom",
                bgcolor="#323130",
                borderwidth=1,
                bordercolor="#6d6d6d",
                font=dict(color="#FFFFFF"),
            ),
        ],
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
     Input('geo', 'value'),
     Input('year','value')]
     )

def update_bar(theme, geo, year):
    municipios,theme_16, theme_17, theme_18 = rankThemes(geo,theme, year)

    traces = []
    traces.append(go.Bar(
        y=theme_16,
        x=municipios,
        xaxis='x2',
        yaxis='y2',
        name = '2016',
        marker=dict(
            color='#1b9e77',
            line=dict(
                color='rgba(91, 207, 135, 2.0)',
                width=0.3),
        ),
        orientation='v',
    )
),

    traces.append(go.Bar(
        y=theme_17,
        x=municipios,
        xaxis='x2',
        yaxis='y2',
        name = '2017',
        marker=dict(
            color='#d95f02',
            line=dict(
                color='rgba(91, 207, 135, 2.0)',
                width=0.3),
        ),
        orientation='v',
    )
),

    traces.append(go.Bar(
        y=theme_18,
        x=municipios,
        xaxis='x2',
        yaxis='y2',
        name = '2018',
        marker=dict(
            color='#7570b3',
            line=dict(
                color='rgba(91, 207, 135, 2.0)',
                width=0.3),
        ),
        orientation='v',
    )
),

    layout = go.Layout(
        title = "Social Vulnerability Index from 2016 to 2018",
        autosize = True,
        yaxis_title = theme,
        xaxis2={
            "title": 'Municipio',
            'zeroline': False,
            "showline": False,
            "showticklabels":True,
            'showgrid':True,
            'domain': [0, 1],
            'side': 'left',
            'anchor': 'x2',
        },

        yaxis2={
            'title': theme,
            'domain': [0, 1],
            'range': [0,1],
            'anchor': 'y2',

        },
        margin=dict(l=100, r=75, t=50, b=110),
        #paper_bgcolor='rgb(204, 204, 204)',
        #plot_bgcolor='rgb(204, 204, 204)',
    )

    return {"data":traces,"layout":layout}

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
