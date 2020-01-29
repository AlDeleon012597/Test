import json
import pandas as pd
import plotly
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html

df = pd.read_csv(r'Municipio_SVI_2018_0.csv')

with open(r'Municipio_SVI_2018.geojson') as json_file:
    pr_data = json.load(json_file)

for feature in pr_data['features']:
    geoid = feature["properties"]['GEOID']
    feature['id'] = geoid

mapbox_accesstoken = 'pk.eyJ1IjoiYWxleGRlbGVvbjEyMyIsImEiOiJjazV1ZWRyanAwYzc2M2pucHVjejdrd2RhIn0.Z1O79Tq170L5eAzyKa-1jQ'
municipio =df['NAME'].str.title().tolist()

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

themes = {'Household Composition and Disability':'HSECOMP',
          'Minority Status and Language':'MINLANG',
          'Housing and Transportiation':'HSETRANS',
          'Socioeconomic Status':'SOCIOECON',
          'Overall Rank':'OVERALL'}

traces = []
# Suburbs order should be the same as "id" passed to location

for theme in themes.items():
    visible = lambda x: True if x == "Household Composition and Disability" else False
    traces.append(go.Choroplethmapbox(
        geojson = pr_data,
        locations = df['GEOID'].tolist(),
        z = df[theme[1]].tolist(),
        colorscale = pl_deep,
        text = municipio,
        colorbar = dict(thickness=20, ticklen=3),
        marker_line_width=0, marker_opacity=0.7,
        visible=visible(theme[0]),
        subplot='mapbox1',
        hovertemplate = "<b>%{text}</b><br><br>" +
                        "Price: %{z}<br>" +
                        "<extra></extra>")) # "<extra></extra>" means we don't display the info in the secondary box, such as trace id.

    themerank = theme[1] + "_rank"
    df[themerank] =df[theme[1]].rank(ascending=False)
    traces.append(go.Bar(
        y=df.sort_values([themerank])["NAME"].tolist()[:40],
        x=df.sort_values([themerank])[theme[1]].tolist()[:40],
        xaxis='x2',
        yaxis='y2',
        marker=dict(
            color='rgba(91, 207, 135, 0.3)',
            line=dict(
                color='rgba(91, 207, 135, 2.0)',
                width=0.7),
        ),
        visible=visible(theme[0]),
        #name='Top 10 suburbs with the highest {} median price'.format(theme[0]),
        orientation='h',
    ))

# Puerto Rico latitude and longitude values

latitude = 18.210445
longitude = -66.487722

layout = go.Layout(
    title = {'text': 'Social Vulnerability Index 2018',
    		 'font': {'size':28,
    		 		  'family':'Arial'}},
    autosize = True,
    mapbox1 = dict(
        domain = {'x': [0.4, 1],'y': [0, .95]},
        center = dict(lat=latitude, lon=longitude),
        accesstoken = mapbox_accesstoken,
        zoom = 7.5),

    xaxis2={
        'zeroline': False,
        "showline": False,
        "showticklabels":True,
        'showgrid':True,
        'domain': [0, 0.3],
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

layout.update(updatemenus=list([

    dict(x=0,
         y=1,
         xanchor='left',
         yanchor='middle',
         buttons=list([
            dict(
                args=['visible', [True, False, False, False, False]],
                label='Household Composition and Disability',
                method='restyle'
                ),
            dict(
                args=['visible', [False, True, False, False, False]],
                label='Minority Status and Language',
                method='restyle'
                ),

            dict(
                args=['visible', [False, False, True, False, False]],
                label='Housing and Transportiation',
                method='restyle'
                ),

            dict(
                args=['visible', [False, False, False, True, False]],
                label='Socioeconomic Status',
                method='restyle'
            ),

            dict(
                args=['visible', [False, False, False, False, True]],
                label='Overall Rank',
                method='restyle'
            )
            ]),
         )]))

fig = go.Figure(data=traces, layout=layout)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Slow code block
app.layout = html.Div(children=[
    html.H1(children=''),
    dcc.Graph(
        id='example-graph-1',
        figure=fig
    ),
    html.Div(children='''
        Data source from CDC @Jan 2020
    ''')
   ])

if __name__ == '__main__':
    app.run_server(debug=True)
