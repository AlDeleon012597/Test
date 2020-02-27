import json
import pandas as pd
import numpy as np
from usgs_api import df_earth
from files import county_geojson,tracts_geojson,tracts_SVI,counties_SVI

def openGeoJson(geoJson_):
    """
    ----------
    Parameters
    ----------
    geoJson_ : geojson
        The geojson of the selected geography (either counties or tracts).
            
    --------
    Returns
    --------
    pr_data: json
        Loaded geojson features and geometries. 
        
    """
    with open(geoJson_) as f:
        pr_data = json.load(f)
        
    return pr_data
    
##ranks and sorts themes for barchart
def rankThemes(geo,theme,year):

    """
    ----------
    Parameters
    ----------
    geo : str
        The name of the type of census geography used. 
        Options include "Tracts" or "County". 
    
    theme: str
        The name of the theme selected.
        There are five possible themes provided in the "themes" dict :
        
            themes = {'Household Composition and Disability':'HSECOMP', 
                      'Minority Status and Language':'MINLANG', 
                      'Housing and Transportiation':'HSETRANS', 
                      'Socioeconomic Status':'SOCIOECON',
                      'Overall Rank':'OVERALL'}  
            
            Structure:  "theme label" as "theme value" --> "theme label" is what is seen by the user and "theme value" is what is used in the backend.
                        See dictionary 

                        1. 'Household Composition and Disability' as 'HSECOMP'
                        2. 'Minority Status and Language' as 'MINLANG'
                        3. 'Housing and Transportiation' as 'HSETRANS'
                        4. 'Socioeconomic Status' as 'SOCIOECON'
                        5. 'Overall Rank' as 'OVERALL'
            
    year: str
        Selected year of the SVI. 
        Bars (of the bar graph) representing the each municipio are sorted by this year.
        
        Possible years:
            
                - 2016
                - 2017
                - 2018
            
    --------
    Returns
    --------
        if "County":
        
            municipios: list                               
                Municipios are first ranked in a dataframe containing the value for the selected SVI theme of the selected year.
                A list of municipio names then sorted and created from this dataframe based on the rank of the selected theme and year.      
            
                For example:
                    Suppose Orocovis scored the highest Overall Rank, Adjuntas the second highest, and Ponce the third.
                    If the "Overall Rank" were selected, then the dataframe would be ranked as follows:
                    
                      
                                    |  Municipio| Rank  |
                                    |-----------+-------|                    
                                    |  Orocovis |   1   |                       
                                    |  Adjuntas |   2   |                   
                                    |  Ponce    |   3   |        
                                    |     .     |   .   |                         
                                    |     .     |   .   |                      
                                    |     .     |   .   | 
                                      
                                          
                    Thus the returned list of names would be in the order of 
                    
                                    ["Orocovis","Adjuntas","Ponce",...]
                                    
        if "Tracts"
            
            municipios: list
                Since Municipios are made up of multiple Census tracts, an average of selected SVI theme values of the census tracts that compose a muncipio is taken.
                The averages are then normalized using min-max scaling.
                
                        min-max:    [x - min(x)]
                                  -----------------
                                  [max(x) - min(x)]
                
                The normalized theme values are then ranked.
                A list of municipio names is then sorted by this rank and the selected year.
                
        theme_16: list
            Returns the a list of values of the selected SVI theme for 2016. 
            This list is sorted by the rank selected SVI theme and year.
            
            If 2017 is selected, then theme_16 is sorted by the values of theme_17.
                
        theme_17: list
            Returns the a list of values of the selected SVI theme for 2017. 
            This list is sorted by the rank selected SVI theme and year.
        
        theme_18: list
            Returns the a list of values of the selected SVI theme for 2018. 
            This list is sorted by the rank selected SVI theme and year.
            

    """
   
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

    """
    ----------
    Parameters
    ----------
    geo : str
        Selected geography (either "Tracts" or "County").
        
    theme : str
        Selected theme (see rankThemes function for description).
            
    --------
    Returns
    --------
    geo: geojson
        The geojson associated with the selected geography.
    
    
    df: dataframe(s)
        The dataframe containing SVI theme values for the selected geography.
        
        If "Tracts" is selected, two data frames are returned-one dataframe for the null values and one for non-null values.
        The dataframe containing null values is titled "df_na".
        The dataframe containing non-null values is titled "df_clean".
       
    text: 
        List of geography names. 
        
    """
    
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


def setRange(lower,upper,col,df = None):
 
    """
    ----------
    Parameters
    ----------
    lower : str
        The lowest value to query for.
    
    upper : str
        The highest value to query for.
    
    col : str
        The column name to perform queries on.
        
    --------
    Returns
    --------
    df_range: dataframe
        A dataframe queried for the inserted lower and upper bound.
        
    """
    
    if lower and not upper:
        df_range = df.loc[lower < df_earth[col] ]
        
    elif not lower and upper:
        df_range = df.loc[df_earth[col] < upper]
        
    elif lower and upper:
        df_range = df.loc[ (lower < df_earth[col]) & (df_earth[col] < upper)]
        
    else:
        df_range = df     
    return df_range

def show_hide(clicks):

    """
    ----------
    Parameters
    ----------
    clicks : int
        The number of times a button is clicked
        
    --------
    Returns
    --------
    
    {'display': 'none'}
        If a button is clicked an even number of times, hide div.
        
    {'display': 'block'}
        If a button is clicked an odd number of times, show div.
        
    """
    
    if not clicks:
        return {'display': 'none'} 
    elif (clicks % 2) == 0:
        return {'display': 'none'} 
    else:
        return {'display': 'block'}