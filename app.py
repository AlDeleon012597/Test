import json
import pandas as pd
import plotly
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input

countys_csv = pd.read_csv(r'G:\Projects\SVI_barchart\Municipio_SVI_2018_0.csv',encoding = 'ISO-8859-1',sep = '\t')
tracts_csv = pd.read_csv(r'G:\Projects\SVI_barchart\Tracts_SVI_2018_0.csv',encoding = 'ISO-8859-1',sep = '\t')

##geojsons for chloropleth map
county_geojson = r'G:\Projects\SVI_barchart\Municipio_SVI_2018.geojson'
tracts_geojson = r'G:\Projects\SVI_barchart\Tracts_SVI_2018.geojson'

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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children=''),
    html.Div([
        dcc.Dropdown(
            id='theme',
            options=[{'label': theme, 'value': themes[theme]} for theme in themes],
            value='HSECOMP'
            ),
        dcc.RadioItems(
            id='geo',
            options=[{'label': i, 'value': i} for i in ['Tracts', 'County']],
            value='Tracts',
            labelStyle={'display': 'inline-block'}
            )]),
    
    dcc.Graph(
        id='pr-chloro'
    ),
    html.Div(children='''
        Data source from CDC @Jan 2020
    ''')
   ])

###helper functions###
def parsegeojson(geo):
    with open(geo) as f:
        pr_data = json.load(f)
        for feature in pr_data['features']:
            geoid = feature["properties"]['GEOID']
            feature['id'] = geoid
    return pr_data

def rankThemes(df_themes,theme):
    themerank = theme + "_rank"
    df_themes[themerank] = df_themes[theme].rank(ascending=False)
    y = df_themes.sort_values([themerank])["NAME"].tolist()[:40]
    x = df_themes.sort_values([themerank])[theme].tolist()[:40]
    return x,y

@app.callback(
    Output('pr-chloro', 'figure'),
    [Input('theme', 'value'),
     Input('geo', 'value')])

def update_graph(theme, geo):
    if geo == 'County':
        geo = county_geojson
        tract  =  False
        df = countys_csv
        text = df['NAME'].str.title().tolist()
        x,y = rankThemes(df,theme)
    if geo == 'Tracts':
        geo = tracts_geojson
        tract = True
        df = tracts_csv
        text = df['Tract_Name'].str.title().tolist()
        avg_themes = df.groupby(['NAME'],as_index=False)['HSECOMP','MINLANG','HSETRANS','SOCIOECON','OVERALL'].mean()
        x,y =rankThemes(avg_themes,theme)

    pr_data = parsegeojson(geo)

    traces = []    
    traces.append(go.Choroplethmapbox(
        geojson = pr_data,
        locations = df['GEOID'].tolist(),
        z = df[theme].tolist(), 
        colorscale = pl_deep,
        text = text, 
        colorbar = dict(thickness=20, ticklen=3),
        marker_line_width=0, marker_opacity=0.7,
        subplot='mapbox1',
        hovertemplate = "<b>%{text}</b><br><br>" +
                        "Price: %{z}<br>" +
                        "<extra></extra>")) # "<extra></extra>" means we don't display the info in the secondary box, such as trace id.
    
    themerank = theme + "_rank"
    df[themerank] =df[theme].rank(ascending=False)
    traces.append(go.Bar(
        y=y,
        x=x,
        xaxis='x2',
        yaxis='y2',
        marker=dict(
            color='rgba(91, 207, 135, 0.3)',
            line=dict(
                color='rgba(91, 207, 135, 2.0)',
                width=0.7),
        ),
        orientation='h',
    ))
    layout = go.Layout(
        title = {'text': 'Social Vulnerability Index 2018',
                     'font': {'size':28, 
                                      'family':'Arial'}},
        autosize = True,
        mapbox1 = dict(
            domain = {'x': [0.3, .7],'y': [.4, .95]},
            center = dict(lat=latitude, lon=longitude),
            accesstoken = mapbox_accesstoken, 
            zoom = 7.5,
            style ='carto-positron'
            ),

        xaxis2={
            'zeroline': False,
            "showline": False,
            "showticklabels":True,
            'showgrid':True,
            'domain': [0, 0.2],
            'side': 'left',
            'anchor': 'x2',
        },

        yaxis2={
            'domain': [0, .95],
            'range': [0,1],
            'anchor': 'y2',
            'autorange': 'reversed',
        },
        margin=dict(l=120, r=50, t=60, b=60),
        paper_bgcolor='rgb(204, 204, 204)',
        plot_bgcolor='rgb(204, 204, 204)',
        height =800
    )
    
    return {"data":traces,"layout":layout}


if __name__ == '__main__':
    app.run_server(debug=True)
