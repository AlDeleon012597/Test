import pandas as pd
import plotly
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from HelperFunctions import openGeoJson,rankThemes,setAttr,setRange,show_hide
from navbar import Navbar
from Options import pl_deep, chloro_colormap, scat_colormap, themes
from usgs_api import df_earth,latitude,longitude,today, min_date
from files import counties_SVI,tracts_SVI
import flask
import io

##mapbox token needed to display pr basemap
mapbox_accesstoken = 'pk.eyJ1IjoiYWxleGRlbGVvbjEyMyIsImEiOiJjazV1ZWRyanAwYzc2M2pucHVjejdrd2RhIn0.Z1O79Tq170L5eAzyKa-1jQ'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

            ################################################
            ############## APPLICATION LAYOUT ##############
            ################################################
            
app.layout = html.Div(children=[
    html.Div([Navbar()], style = {'backgroundColor':'purple'}, className = 'navbar'),
    html.Img(className="logo", src=app.get_asset_url("Centro_Logo.png")),
    html.H1(id = "title", children='Hazard Vulnerability'),
    #dcc.Tabs(id = ')
    html.Div([
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
                                                    id='button_svi',
                                                    className = 'button'),
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
                                        
                                        html.Button("Map Filters:", 
                                                    id='button_map',
                                                    className = 'button'),
                                        html.Div([
                                            
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
                                             ],
                                            style= {'display': 'block'},
                                            id = 'map_div'
                                        ),
                                        
                                        html.Button("Earth Quake Filters:", 
                                                    id='button_eq',
                                                    className = 'button'),
                                        html.Div([
                                            
                                            html.P(
                                                 "Specify Earthquake magnitude:",
                                                 className = "control_label "
                                                 ),
                                                 
                                            dcc.Input(
                                                id="_min",
                                                type="number",
                                                debounce=True,
                                                placeholder="Min",
                                                min = 2,
                                                max = 6,
                                                step = .5,
                                                className = "filter_control",
                                                ),
                                                
                                            dcc.Input(
                                                id="_max",
                                                type="number",
                                                placeholder="Max",
                                                min=5,
                                                max=10,
                                                step = .5,
                                                className = "filter_control",
                                                ),
                                                
                                            dcc.DatePickerRange(
                                                    id='date-picker',
                                                    className = 'filter_control',
                                                    min_date_allowed=min_date,
                                                    max_date_allowed=today,
                                                    initial_visible_month=today,
                                                    end_date=today,
                                                    start_date = min_date,
                                                    
                                                ),
                                            ],
                                            style= {'display': 'block'},
                                            id = 'eq_div'
                                        ),  
                                    ]
                                ),   
                        dcc.Tab(
                            label='Data',
                            value='tab-3',
                            children = [
                                        dcc.Dropdown(id='my-dropdown', 
                                                    value='default',
                                                    options=[
                                                             {'label': 'SVI Tracts', 'value': "tracts_svi"},
                                                             {'label': 'SVI Counties', 'value': "counties_SVI"},
                                                             {'label': 'USGS Earthquakes', 'value':'USGS Earthquakes' }
                                                         ]
                                                    ),
                                        html.A('Download CSV', 
                                                id='my-link'
                                            ),      
                                        ],
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
        className = "container-display"
        )
    ],
)


        #########################################
        ############ APP CALLBACKS ##############
        #########################################

@app.callback(
   Output(component_id='eq_div', component_property='style'),
   [Input(component_id='button_eq', component_property='n_clicks')]
   )

def show_hide_element(eq_clicks):
    return show_hide(eq_clicks)
        
@app.callback(
   Output(component_id='map_div', component_property='style'),
   [Input(component_id='button_map', component_property='n_clicks')]
   )

def show_hide_element(map_clicks):
    return show_hide(map_clicks)
        
@app.callback(
   Output(component_id='svi_div', component_property='style'),
   [Input(component_id='button_svi', component_property='n_clicks')]
   )

def show_hide_element(svi_clicks):
    return show_hide(svi_clicks)

@app.callback(
    dash.dependencies.Output('datatable-interactivity', 'data'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('_min', 'value'),
     Input('_max', 'value')]
     )
def updatetable(start, end,_min,_max):
    df_time = setRange(start,end,'time',df = df_earth,)
    df_mags = setRange(_min,_max,'mag',df = df_earth,)
    return df_mags.to_dict('records')
    

@app.callback(
    dash.dependencies.Output('mag_scat', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date'),
     Input('_min', 'value'),
     Input('_max', 'value')]
     )

def updatescatterplot(start, end,_min,_max):
    df_mags = setRange(_min,_max,'mag',df = df_earth)
    df_time = setRange(start,end,'time',df = df_earth)
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
        df_mags = setRange(_min,_max,'mag',df = df_earth)
        for mag_range in chloro_colormap:
            if mag_range == (5.0,10):
                name = "{} {}".format(mag_range[0],"and up")
            else:   
                name = "{0} to {1}".format(mag_range[0],mag_range[1])
            df_mags_range = df_mags.loc[(df_mags['mag'] >= mag_range[0]) & (df_mags['mag']<mag_range[1])]
            
            traces.append(go.Scattermapbox(
                lat=df_mags_range['lat'],
                lon=df_mags_range['long'],
                mode='markers',
                marker={"color":chloro_colormap[mag_range]['color'],
                            "size":chloro_colormap[mag_range]['size'],
                            "opacity": 1},   
                name = "{0} to {1}".format(mag_range[0],mag_range[1]),            
                text= df_mags_range[['place','mag']],
                texttemplate = "%Name:%{df_mags_range['place']}\nMagnitude:%{df_mags_range['mag']}",
                showlegend = True,
            ))
            
    if "SVI" in layers:
        geoJson,df_chloro,text = setAttr(geo,theme) 
        geoJson = openGeoJson(geoJson)
    
        traces.append(go.Choroplethmapbox(
            geojson = geoJson,
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
                geojson = geoJson,
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
    
@app.callback(Output('my-link', 'href'), 
    [Input('my-dropdown', 'value')])
def update_link(value):
    return '/dash/urlToDownload?value={}'.format(value)


@app.server.route('/dash/urlToDownload')
def download_csv():
    value = flask.request.args.get('value')
    # create a dynamic csv or file here using `StringIO`
    # (instead of writing to the file system)
    str_io = io.StringIO()
    str_io.write('You have selected {}'.format(value))
    mem = io.BytesIO()
    mem.write(str_io.getvalue().encode('ISO-8859-1'))
    mem.seek(0)
    str_io.close()
    return flask.send_file(mem,
                           mimetype='text/csv',
                           attachment_filename='downloadFile.csv',
                           as_attachment=True)
                           
if __name__ == '__main__':
    app.run_server(debug=True)
