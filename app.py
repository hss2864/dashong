#!/usr/bin/env python
# coding: utf-8

# In[1]:


### Call packages
import pandas as pd
import numpy as np
import os
import io
import glob
import datetime
import calendar     
import geopandas as gpd
import requests

# Dash & Plotly for visualization
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table as dt
import plotly.graph_objects as go


# In[2]:


# path = 'Data/'
path = 'C:/Users/HONG/Desktop/github/dashong/Data/'


# ### Covid Data

# In[3]:


data = pd.read_csv(path + 'COVID/dashboard_data.csv')
data['date'] = pd.to_datetime(data['date'])
update = data['date'].dt.strftime('%Y-%m-%d').iloc[-1]


# In[4]:


dash_colors = {
    'background': '#ffffff',
    'text': '#000000',
    'grid': '#e6e6e6',
    'red': '#f50000',
    'blue': '#0054ff',
    'green': '#41e86e'
}

states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
          'Colorado', 'Connecticut', 'Delaware', 'District of Columbia',
          'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana',
          'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
          'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
          'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
          'New Jersey', 'New Mexico', 'New York', 'North Carolina',
          'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
          'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee',
          'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
          'West Virginia', 'Wisconsin', 'Wyoming']


# In[5]:


# US
df_us = pd.read_csv(path + 'COVID/df_us.csv')
df_us['percentage'] = df_us['percentage'].astype(str)
df_us_full = data[data['Country/Region'] == 'US']


# In[6]:


# World
df_world = pd.read_csv(path + 'COVID/df_worldwide.csv')
df_world['percentage'] = df_world['percentage'].astype(str)


# ### Covid Map

# In[7]:


route = 'CENSUS/'
shp = glob.glob(path + route + '*.shp')[0]
usa = gpd.read_file(shp)
usa.head(1)

# cumulative sum by state
df_m = df_us_full.groupby('Province/State').agg(
    con=pd.NamedAgg(column='Confirmed', aggfunc=sum),
    dea=pd.NamedAgg(column='Deaths', aggfunc=sum)
)
df_m['NAME'] = df_m.index 
df_m = df_m[(df_m['NAME']!='Recovered') & (df_m['con']>0)].reset_index(drop=True)
# hover text
df_m['text'] = df_m['NAME'] + '<br>' + 'Confirmed = ' +  df_m['con'].apply(lambda x : "{:,}".format(x)).apply(lambda x: str(x)) + '<br>' + 'Deaths = ' +  df_m['dea'].apply(lambda x : "{:,}".format(x)).apply(lambda x: str(x))
# merge usa map
df_m1 = pd.merge(usa, df_m, how='left', on='NAME')


# ### Unemployment Data

# In[8]:


file_list = glob.glob(path+'BLS/lau_*.csv')
df_lau = pd.read_csv(file_list[-1])
del(file_list)
df_lau['time'] = df_lau['year'].astype(str) + '-' + df_lau['period'].str[1:3]
df_lau['time'] = pd.to_datetime(df_lau.time, dayfirst=True)


# ### GDP Data

# In[9]:


route = 'BEA/'
file_list = glob.glob(path + route +'realgdp_*.csv')
df_gdp = pd.read_csv(file_list[-1])
del(file_list)
# wide -> long
df_gdp2 = df_gdp.copy()
df_gdp2 = pd.melt(df_gdp2, id_vars = ['LineNumber', 'SeriesCode', 'LineDescription'], var_name='Time', value_name='Value')
indexs = df_gdp2['LineDescription'].unique()


# ### Covid Table Data

# In[10]:


df=df_us_full
# cumulative sum by state
t_c = df.groupby(by='Province/State', as_index=False)['Confirmed'].sum().sort_values(by='Province/State')
t_a = df.groupby(by='Province/State', as_index=False)['Active'].sum().sort_values(by='Province/State')
t_d = df.groupby(by='Province/State', as_index=False)['Deaths'].sum().sort_values(by='Province/State')
del(df)
# concatenate dataset
df_t = pd.concat([t_c, t_a, t_d], axis=1)
df_t = df_t.loc[:,~df_t.columns.duplicated()].sort_values(by='Confirmed', ascending=False)
df_t = df_t[(df_t['Province/State']!='Recovered') & (df_t['Confirmed']>0)].reset_index(drop=True)
df_t['Fatality Rate(%)'] = round(df_t['Deaths']/df_t['Confirmed']*100, 2)
# delimiter
df_t['Confirmed'] = df_t['Confirmed'].apply(lambda x : "{:,}".format(x))
df_t['Active'] = df_t['Active'].apply(lambda x : "{:,}".format(x))
df_t['Deaths'] = df_t['Deaths'].apply(lambda x : "{:,}".format(x))
df_t['Fatality Rate(%)'] = df_t['Fatality Rate(%)'].apply(lambda x : "{:.2f}".format(x))


# ### Covid Deaths Age, Sex Data3

# In[11]:


route = 'CDC/'
file_list = glob.glob(path + route +'*_week_*.csv')
df_s_a = pd.read_csv(file_list[-1])
del(file_list)
age_n = df_s_a['age_group'].unique()
sex_n = df_s_a['sex'].unique()


# In[ ]:





# # App_Dash

# In[66]:


app = dash.Dash()
app.layout = html.Div([
    
    # Tab start
    dcc.Tabs([
        ##### Tab1 : Covid 19 - Status #####
        dcc.Tab(label='COVID-19 Trend',
                children=[
                        
                     html.Div([
                         
                        ## Left ##
                        html.Div(
                            className='columns',
                            children=[
                            
                            # Graph 1 - KPIs
                            html.Div([
                                
                                # Title
                                html.H3(children = 'World vs USA', style = {'textAlign': 'center', 'margin': '15'}),
                                
                                # dumy dropdown invisible ***
                                dcc.Dropdown(id = 'id_stat_tmp',
                                             options=[{'label':i, 'value':i} for i in states],
                                             value = 'United States',
                                             style={'width':'40%', 'display': 'none'}),
                                
                                html.Div([
                                    html.Label('World', style={'font-family':'Arial', 'font-size':'70', 'font-weight':'bold'}),
                                    dcc.Graph(id='cum_g'), # Confirmed
                                    dcc.Graph(id='cur_g'), # Currently Active
                                    dcc.Graph(id='death_g'), # Deaths
                                    dcc.Graph(id='recover_g'), # Recovered
                                    dcc.Graph(id='fatal_g') # Fatality
                                ], style={'width':'50%', 'textAlign':'center', 'display':'inline-block'}),
                                
                                html.Div([
                                    html.Label('United States', style={'font-family':'Arial', 'font-size':'70', 'font-weight':'bold'}),
                                    dcc.Graph(id='cum_u'), # Confirmed
                                    dcc.Graph(id='cur_u'), # Currently Active
                                    dcc.Graph(id='death_u'), # Deaths
                                    dcc.Graph(id='recover_u'), # Recovered
                                    dcc.Graph(id='fatal_u') # Fatality
                                ], style={'width':'50%', 'textAlign':'center', 'display':'inline-block'}),
                                
                                ]),
                            ], style={'float':'left', 'width':'20%', 'display':'inline-block'}
                        ),
                        
                         
                        ## middle ##
                        html.Div(
                            className='columns',
                            children=[
                                
                                # Title
                                html.H3(children = 'USA', style = {'textAlign': 'center', 'margin': '15'}),
                                
                                # Graph 2 - Line
                                dcc.Graph(id='covid_line', style={'width':'100%', 'display':'inline-block'})
                            ], style={'float':'left', 'width':'40%', 'display':'inline-block'}
                        ),
                                
                                
                        ## Right ##
                        html.Div(
                            className='columns',
                            children=[
                            
                                # Title
                                html.H3(children = 'USA - Covid Map', style = {'textAlign': 'center', 'margin': '15'}),
  
                                # Graph1 -  Map
                                dcc.Graph(id='covid_map', 
                                          figure = {'data': [go.Choropleth(locations = df_m1['STUSPS'], # location
                                                                           z = df_m1['con'],            # values
                                                                           locationmode = 'USA-states', # set of locations match entries in `locations`
                                                                           colorscale = 'Reds',         # scale color
                                                                           marker_line_color='white',   # boundary color
                                                                           hoverinfo = 'text',
                                                                           text = df_m1['text'])],
                                                    'layout': go.Layout(geo_scope = 'usa',
                                                                        title = {'text':'COVID-19 US Cumulative Cases by County'})}),
                            ], style={'float':'left', 'width':'40%', 'display':'inline-block'}),
                        ]),
                    ]
               ),
        
        
        
        ##### Tab2 : Covid 19 - States & Sex & Age #####
        dcc.Tab(label='States, Sex, Age with COVID-19',
                children=[
                         
                    ## 1 row, 2 columns ##
                    html.Div(
                        className='row-1',
                        children=[
                            
                        # Graph 1 - Bar & Table
                        html.Div([
                                
                            # Title
                            html.H3(children = 'Cases by State', style = {'textAlign': 'center', 'margin': '15'}),
                            
                            # Dropdown
                            html.Label('States:'), 
                            dcc.Dropdown(id = 'id_stat',
                                         options=[{'label':i, 'value':i} for i in states],
                                         value = 'United States',
                                         style={'width':'40%'}),
                            
                            # Bar & Table
                            html.Div([

                                # 1) Daily chart
                                dcc.Graph(id='covid_daily')
                                ], style={'float':'left', 'width':'50%', 'font-family':'Arial', 'display':'inline-block'}),

                                # 2) Table
                                html.Div(
                                    dt.DataTable(id='covid_table',
                                                 columns=[{"name": i, "id": i} for i in df_t.columns],
                                                 data=df_t.to_dict("rows"),
                                                 style_as_list_view=True,
                                                 style_table={'overflowY':'scroll', 'height':300},  # 지정안하면 최소 500 시작
                                                 style_header={'fontWeight': 'bold', 'textAlign':'center',
                                                               'border': 'thin lightgrey solid',
                                                               'backgroundColor': 'forestgreen',
                                                               'color': 'white', 'minWidth': 95, 'maxWidth': 150},
                                                 fixed_rows={'headers': True, 'data': 0},
                                                 style_cell={'minWidth': 95, 'maxWidth': 150}),
                                    style={'float':'right', 'width':'50%', 'display':'inline-block'})
                                ])
                            ]),
                    
                    
                     ## 2 row, 2 columns ##
                     html.Div(
                            className='row-2',
                            children=[
                                
                            # Graph 1 - Bar & Table
                            html.Div([
                                
                                # Title
                                html.H3(children = 'Provisional Death Counts for COVID-19', style = {'textAlign': 'center', 'margin': '15'}),
                                
                                # Dropdown
                                dcc.Dropdown(id = 'id_age',
                                             options=[{'label':i, 'value':i} for i in sex_n],
                                             value = 'All Sex',
                                             style={'width':'40%'}),
                                
                                # Graph 2 - Line & Pie
                                html.Div([
                                    
                                    # 1) Line
                                    html.Div([
                                        dcc.Graph(id='age_line')
                                        ], style={'width':'70%', 'font-family':'Arial', 'display':'inline-block'}),
                                
                                    # 2) Pie
                                    html.Div([
                                        dcc.Graph(id='sex_pie')
                                        ], style={'width':'30%', 'font-family':'Arial', 'display':'inline-block'})
                                    ])
                                ])
                            ]),
                ]
           ),
        
        
        
        ##### Tab3 : Economic #####
        dcc.Tab(label='Economic impact with COVID-19',
                children=[
                    
                    ## Left ##        
                    html.Div(
                        className='col-1',
                        children=[
                            
                            html.Div([
                                # Title
                                html.H3(children = 'Unemployment Statistics', style = {'textAlign': 'center', 'margin': '15'}),
                                
                                # Dropdown
                                html.Label('States:'), 
                                dcc.Dropdown(id = 'id_stat2',
                                             options=[{'label':i, 'value':i} for i in states],
                                             value = 'United States',
                                             style={'width':'90%'}),
                                
                                html.Div([

                                    ########## Covid & Unemployment Rate line chart ##########
                                    html.Div([
                                        dcc.Graph(id='g_line')], style={'height':300}),

                                    ########## LAU _ 3 line chart ##########
                                    html.Div([
                                        html.Div(
                                            # employment
                                            dcc.Graph(id='g_em'),
                                            style={'width':'33%', 'display':'inline-block', 'height':300}
                                        ),
                                        html.Div(
                                            # unemployment
                                            dcc.Graph(id='g_un'),
                                            style={'width':'33%', 'display':'inline-block', 'height':300}
                                        ),
                                        html.Div(
                                            # rate
                                            dcc.Graph(id='g_r'),
                                            style={'width':'33%', 'display':'inline-block', 'height':300}
                                        )], className="row")
                                    ])
                            ])
                        ], style={'float':'left', 'width':'60%', 'display':'inline-block'}),
                        
                    
                    ## Right ##
                    html.Div(
                        className='col-2',
                        children=[

                            html.Div([

                                # Title
                                html.H3(children = 'GDP', style = {'textAlign': 'center', 'margin': '15'}),

                                # Dropdown - gdp indexs
                                html.Label('Indexs:'), 
                                dcc.Dropdown(id = 'id_index',
                                             options=[{'label':i, 'value':i} for i in indexs],
                                             value = 'Gross domestic product',
                                             style={'width':'100%'}),

                                ########## gdp line chart ##########
                                html.Div([
                                    dcc.Graph(id='bar_gdp')])
                            ])
                        ], style={'width':'40%', 'display':'inline-block'}),
            ]),
        
        
        
        ##### Tab4 : Info #####
        dcc.Tab(label='About this site',
               children=[
                    html.Div(dcc.Markdown('''
                    ## Last Updates
                    The JOHNS HOPKINS COVID-19 Data: 6/8/2020
                    
                    The Provisional COVID-19 Death by Sex and Age Data: 5/30/2020
                    
                    The Unemployment Data: 5/22/2020
                    
                    The GDP Data: 5/28/2020
                    
                    App: 6/5/2020
                    
                    ## Summary
                    This is interactive web dashboard to view COVID-19 and Economic-Impact data from across the United States. We used the public data and  deployed on Heroku with Python and Dash.
                    
                    As the coronavirus continues to spread throughout the U.S., we have used this dashboard to understand how the coronavirus are economically impacted.
                    
                    ## Source Data
                    **Overall COVID-19 cases:** [Johns Kopkins CSSE](https://github.com/CSSEGISandData/COVID-19) (Next update: Every day)
                    
                    **U.S. deaths by sex and age:** [Centers for Disease Control and Prevention(CDC)](https://data.cdc.gov/NCHS/Provisional-COVID-19-Death-Counts-by-Sex-Age-and-W/vsak-wrfu) (Next update: Every week)
                    
                    **U.S. unemployment rate:** [Bureau of Labor Statistics(BLS)](https://www.bls.gov/lau/) (Next update: Every month - 6/19/2020)
                    
                    **U.S. GDP:** [Bureau of Economic Analysis(BEA)](https://www.bea.gov/) (Next update: Every month - 6/25/2020)
                    
                    The data ETL process and some charts are referenced [here](https://github.com/raffg/covid-19).
                    
                    ## Code
                    Instructions and feature document [here](https://github.com/hss2864/dashong).
                    
                    ## Contributors
                    Kyungtae Kim, PhD; Sungjun Hong, MS; Sungsoo Hong, BS; Don Kim; Kyu Kim
                    ''')
                            )], style={'font-family':'Arial', 'font-size':'25', 'display': 'inline-block'})
    ])
])


# In[67]:


#################### [Tab1 : Covid 19] ####################

############# World #############
#################
### Confirmed ###
#################
@app.callback(Output('cum_g', 'figure'), [Input('id_stat', 'value')])
def confirmed(val):
    df = df_world      
    value = df[df['date'] == df['date'].iloc[-1]]['Confirmed'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Confirmed'].sum()
    # Data
    trace1 = {'type': 'indicator',
              'mode': 'number+delta',
              'value': value,
              'delta': {'reference': delta,
                        'valueformat': ',g',
                        'relative': False,
                        'increasing': {'color': dash_colors['red']},
                        'decreasing': {'color': dash_colors['blue']},
                        'font': {'size': 15}},
              'number': {'valueformat': ',',
                         'font': {'size': 25}},
              'domain': {'y': [0, 1], 'x': [0, 1]}}
    data = [trace1]
    # Layout
    layout = go.Layout(title={'text': "Confirmed"},
                       font=dict(color='black'),
                       height=100)
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


###############
### Active  ###
###############
@app.callback(Output('cur_g', 'figure'), [Input('id_stat', 'value')])
def confirmed(val):
    df = df_world
    value = df[df['date'] == df['date'].iloc[-1]]['Active'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Active'].sum()
    # Data
    trace1 = {'type': 'indicator',
              'mode': 'number+delta',
              'value': value,
              'delta': {'reference': delta,
                        'valueformat': ',g',
                        'relative': False,
                        'increasing': {'color': dash_colors['red']},
                        'decreasing': {'color': dash_colors['blue']},
                        'font': {'size': 15}},
              'number': {'valueformat': ',',
                         'font': {'size': 25}},
              'domain': {'y': [0, 1], 'x': [0, 1]}}
    data = [trace1]
    # Layout
    layout = go.Layout(title={'text': "Active"},
                       font=dict(color='black'),
                       height=100)
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


###############
### Deaths  ###
###############
@app.callback(Output('death_g', 'figure'),[Input('id_stat', 'value')])
def confirmed(val):
    df = df_world
    value = df[df['date'] == df['date'].iloc[-1]]['Deaths'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Deaths'].sum()
    # Data
    trace1 = {'type': 'indicator',
              'mode': 'number+delta',
              'value': value,
              'delta': {'reference': delta,
                        'valueformat': ',g',
                        'relative': False,
                        'increasing': {'color': dash_colors['red']},
                        'decreasing': {'color': dash_colors['blue']},
                        'font': {'size': 15}},
              'number': {'valueformat': ',',
                         'font': {'size': 25}},
              'domain': {'y': [0, 1], 'x': [0, 1]}}
    data = [trace1]
    # Layout
    layout = go.Layout(title={'text': "Deaths"},
                       font=dict(color=dash_colors['red']),
                       height=100)
    
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


##################
### Recovered  ###
##################
@app.callback(Output('recover_g', 'figure'),[Input('id_stat', 'value')])
def confirmed(val):
    df = df_world
    value = df[df['date'] == df['date'].iloc[-1]]['Recovered'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Recovered'].sum()
    # Data
    trace1 = {'type': 'indicator',
              'mode': 'number+delta',
              'value': value,
              'delta': {'reference': delta,
                        'valueformat': ',g',
                        'relative': False,
                        'increasing': {'color': dash_colors['green']},
                        'decreasing': {'color': dash_colors['blue']},
                        'font': {'size': 15}},
              'number': {'valueformat': ',',
                         'font': {'size': 25}},
              'domain': {'y': [0, 1], 'x': [0, 1]}}
    data = [trace1]
    # Layout
    layout = go.Layout(title={'text': "Recovered"},
                       font=dict(color='black'),
                       height=100)
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


#################
### Fatality  ###
#################
@app.callback(Output('fatal_g', 'figure'),[Input('id_stat', 'value')])
def confirmed(val):
    df = df_world
    value = df[df['date'] == df['date'].iloc[-1]]['Deaths'].sum() / df[df['date'] == df['date'].iloc[-1]]['Confirmed'].sum()
    # Data
    trace1 = {'type': 'indicator',
              'mode': 'number',
              'value': round(value * 100, 2),
              'number': {'valueformat': ',', 'suffix':'%',
                         'font': {'size': 25}},
              'domain': {'y': [0, 1], 'x': [0, 1]}}
    data = [trace1]
    # Layout
    layout = go.Layout(title={'text': "Fatality Rate"},
                       font=dict(color='black'),
                       height=100)
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


############# US #############
#################
### Confirmed ###
#################
@app.callback(Output('cum_u', 'figure'), [Input('id_stat', 'value')])
def confirmed(val):
    df = df_us_full        
    value = df[df['date'] == df['date'].iloc[-1]]['Confirmed'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Confirmed'].sum()
    # Data
    trace1 = {'type': 'indicator',
              'mode': 'number+delta',
              'value': value,
              'delta': {'reference': delta,
                        'valueformat': ',g',
                        'relative': False,
                        'increasing': {'color': dash_colors['red']},
                        'decreasing': {'color': dash_colors['blue']},
                        'font': {'size': 15}},
              'number': {'valueformat': ',',
                         'font': {'size': 25}},
              'domain': {'y': [0, 1], 'x': [0, 1]}}
    data = [trace1]
    # Layout
    layout = go.Layout(title={'text': "Confirmed"},
                       font=dict(color='black'),
                       height=100)
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


###############
### Active  ###
###############
@app.callback(Output('cur_u', 'figure'), [Input('id_stat', 'value')])
def confirmed(val):
    df = df_us_full
    value = df[df['date'] == df['date'].iloc[-1]]['Active'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Active'].sum()
    # Data
    trace1 = {'type': 'indicator',
              'mode': 'number+delta',
              'value': value,
              'delta': {'reference': delta,
                        'valueformat': ',g',
                        'relative': False,
                        'increasing': {'color': dash_colors['red']},
                        'decreasing': {'color': dash_colors['blue']},
                        'font': {'size': 15}},
              'number': {'valueformat': ',',
                         'font': {'size': 25}},
              'domain': {'y': [0, 1], 'x': [0, 1]}}
    data = [trace1]
    # Layout
    layout = go.Layout(title={'text': "Active"},
                       font=dict(color='black'),
                       height=100)
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


###############
### Deaths  ###
###############
@app.callback(Output('death_u', 'figure'),[Input('id_stat', 'value')])
def confirmed(val):
    df = df_us_full
    value = df[df['date'] == df['date'].iloc[-1]]['Deaths'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Deaths'].sum()
    # Data
    trace1 = {'type': 'indicator',
              'mode': 'number+delta',
              'value': value,
              'delta': {'reference': delta,
                        'valueformat': ',g',
                        'relative': False,
                        'increasing': {'color': dash_colors['red']},
                        'decreasing': {'color': dash_colors['blue']},
                        'font': {'size': 15}},
              'number': {'valueformat': ',',
                         'font': {'size': 25}},
              'domain': {'y': [0, 1], 'x': [0, 1]}}
    data = [trace1]
    # Layout
    layout = go.Layout(title={'text': "Deaths"},
                       font=dict(color=dash_colors['red']),
                       height=100)
    
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


##################
### Recovered  ###
##################
@app.callback(Output('recover_u', 'figure'),[Input('id_stat', 'value')])
def confirmed(val):
    df = df_us_full
    value = df[df['date'] == df['date'].iloc[-1]]['Recovered'].sum()
    delta = df[df['date'] == df['date'].unique()[-2]]['Recovered'].sum()
    # Data
    trace1 = {'type': 'indicator',
              'mode': 'number+delta',
              'value': value,
              'delta': {'reference': delta,
                        'valueformat': ',g',
                        'relative': False,
                        'increasing': {'color': dash_colors['green']},
                        'decreasing': {'color': dash_colors['blue']},
                        'font': {'size': 15}},
              'number': {'valueformat': ',',
                         'font': {'size': 25}},
              'domain': {'y': [0, 1], 'x': [0, 1]}}
    data = [trace1]
    # Layout
    layout = go.Layout(title={'text': "Recovered"},
                       font=dict(color='black'),
                       height=100)
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


#################
### Fatality  ###
#################
@app.callback(Output('fatal_u', 'figure'),[Input('id_stat', 'value')])
def confirmed(val):
    df = df_us_full
    value = df[df['date'] == df['date'].iloc[-1]]['Deaths'].sum() / df[df['date'] == df['date'].iloc[-1]]['Confirmed'].sum()
    # Data
    trace1 = {'type': 'indicator',
              'mode': 'number',
              'value': round(value * 100, 2),
              'number': {'valueformat': ',', 'suffix':'%',
                         'font': {'size': 25}},
              'domain': {'y': [0, 1], 'x': [0, 1]}}
    data = [trace1]
    # Layout
    layout = go.Layout(title={'text': "Fatality Rate"},
                       font=dict(color='black'),
                       height=100)
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


########################
### Covid Line Chart ###
########################
@app.callback(Output('covid_line', 'figure'),[Input('id_stat', 'value')])
def trend_line(val):
    df = df_us_full
    # Confirmed
    trace1 = go.Scatter(x=df.groupby('date')['date'].first(),
                        y=df.groupby('date')['Confirmed'].sum(),
                        hovertemplate='%{y:,g}',
                        name="Confirmed",
                        mode='lines')
    # Active
    trace2 = go.Scatter(x=df.groupby('date')['date'].first(),
                        y=df.groupby('date')['Active'].sum(),
                        hovertemplate='%{y:,g}',
                        name="Active",
                        mode='lines')
    # Recovered
    trace3 = go.Scatter(x=df.groupby('date')['date'].first(),
                        y=df.groupby('date')['Recovered'].sum(),
                        hovertemplate='%{y:,g}',
                        name="Recovered",
                        mode='lines')
    # Deaths
    trace4 = go.Scatter(x=df.groupby('date')['date'].first(),
                        y=df.groupby('date')['Deaths'].sum(),
                        hovertemplate='%{y:,g}',
                        name="Deaths",
                        mode='lines')
    data = [trace1, trace2, trace3, trace4]
    # Layout
    layout = go.Layout(title="United States Infections",
                       xaxis_title="Date",
                       yaxis_title="Number of Cases",
                       font=dict(color=dash_colors['text']),
                       paper_bgcolor=dash_colors['background'],
                       plot_bgcolor=dash_colors['background'],
                       xaxis=dict(gridcolor=dash_colors['grid']),
                       yaxis=dict(gridcolor=dash_colors['grid']),
                       height=500)
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


# In[68]:


#################### [Tab2 : Covid 19 by States / Sex / Age] ####################

#######################
### Covid Daily Bar ###
#######################
@app.callback(Output('covid_daily', 'figure'), [Input('id_stat', 'value')])
def daily_bar(val):
    if val == 'United States':
        df = df_us_full
    else:
        df = df_us_full[df_us_full['Province/State']==val]
    con_ = df[df['date'] == df['date'].unique()[-2]]['Confirmed'].sum()
    act_ = df[df['date'] == df['date'].unique()[-2]]['Active'].sum()
    dea_ = df[df['date'] == df['date'].unique()[-2]]['Deaths'].sum()
    rec_ = df[df['date'] == df['date'].unique()[-2]]['Recovered'].sum()
    # Data
    trace1 = go.Bar(x = [dea_, rec_, act_, con_],
                    y = ['Deaths', 'Recorvered', 'Active', 'Confirmed'],
                    text = ['Deaths', 'Recorvered', 'Active', 'Confirmed'],
                    marker_color = ['#d62728', '#2ca02b', '#ff7f0e', '#1f77b4'],
                    orientation = 'h')
#     {'color': dash_colors['blue']
    data=[trace1]
    # Layout
    layout = go.Layout(hovermode = 'closest',
                       legend={'orientation':'h'},
                       yaxis = {'showgrid': False},
                       xaxis = {'tickformat': ',d', 'showgrid': False},
                       title={'text': 'Daily COVID-19 :' + val},
                       paper_bgcolor=dash_colors['background'],
                       plot_bgcolor=dash_colors['background'],
                       height=300)
   # Figure
    figure = {'data': data, 'layout': layout}
    return figure

#####################
### Deaths by Age ###
#####################
@app.callback(Output('age_line', 'figure'),[Input('id_age', 'value')])
def death_sex(val):
    df1 = df_s_a[df_s_a['sex']==val]
    trace = []
    # draw and append traces for each state
    for gr in age_n:
        trace.append(go.Scatter(x = df1[df1['age_group'] == gr]['week_ending_date'],
                                y = df1[df1['age_group'] == gr]['covid_19_deaths'],
                                hovertemplate='%{y:,g}',
                                mode = 'lines',
                                marker = {'size':10},
                                name = gr))
    traces = [trace]
    data = [val for sublist in traces for val in sublist]

    layout = go.Layout(
        height = 300,
        hovermode = 'closest',
        title='by Age',
        yaxis_title="Number of Deaths",
        font=dict(color=dash_colors['text']),
        paper_bgcolor=dash_colors['background'],
        plot_bgcolor=dash_colors['background'],
        yaxis=dict(gridcolor=dash_colors['grid']))
    
    # define figure
    figure = {'data': data, 'layout': layout}
    
    return figure

#####################
### Deaths by Sex ###
#####################
@app.callback(Output('sex_pie', 'figure'),[Input('id_age', 'value')])
def death_age(val):
    df1 = df_s_a[df_s_a['sex']!='All Sex']
    values = [df1[df1['sex']=='Male']['covid_19_deaths'].sum(), df1[df1['sex']=='Female']['covid_19_deaths'].sum()]
    labels = ['Male', 'Female']
    
    # pie chart
    trace = go.Pie(labels=labels,
                   values=values,
                   textinfo='label+percent',
                   insidetextorientation='radial',
                   hole=0.6, showlegend=False)
    data = [trace]

    layout = go.Layout(
        height = 300,
        hovermode = 'closest',
        title='by Sex',
        font=dict(color=dash_colors['text']))
    
    # define figure
    figure = {'data': data, 'layout': layout}
    
    return figure


# In[69]:


############################## [Tab3 : Economic] ##############################

############################################
### Covid & Unemployment Rate Line Chart ###
############################################
@app.callback(
    Output('g_line', 'figure'), [Input('id_stat2', 'value')])
def trend_line(val):
    if val == 'United States':
        df = df_us_full
    else:
        df = df_us_full[df_us_full['Province/State']==val]
    
    df1 = df_lau[(df_lau['state_nm']==val) & (df_lau['time'] >= "2020")]
    g_r = df1[df1['type']=='Rate']
    # Data; Confirmed & Unemployment Rate
    trace1 = go.Scatter(x=df.groupby('date')['date'].first(),
                        y=df.groupby('date')['Confirmed'].sum(),
                        hovertemplate='%{y:,g}',
                        name="Confirmed",
                        mode='lines')
    trace2 = go.Scatter(x = g_r['time'],
                        y = g_r['value'],
                        yaxis='y2',
                        mode = 'lines+markers',
                        marker = {'size':10},
                        name = 'Unemployment Rate')
    data = [trace1, trace2]
    # Layout
    layout = go.Layout(title="Unemployment Rates vs. COVID-19 Infections",
                       xaxis_title="Date",
                       yaxis_title="Number of Cases",
                       font=dict(color=dash_colors['text']),
                       paper_bgcolor=dash_colors['background'],
                       plot_bgcolor=dash_colors['background'],
                       xaxis=dict(gridcolor=dash_colors['grid']),
                       yaxis=dict(gridcolor=dash_colors['grid']),
                       yaxis2=dict(overlaying='y', side='right', showgrid=False))
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


########################
### LAU - Employment ###
########################
@app.callback(Output('g_em', 'figure'), [Input('id_stat2', 'value')])
def update_output(val):
    df1 = df_lau[(df_lau['state_nm']==val) & (df_lau['time'] >= "2018")]
    g_e = df1[df1['type']=='Employment']
    # Data
    trace = go.Scatter(x = g_e['time'],
                       y = g_e['value'],
                       mode = 'lines',
                       name = 'Employment')        
    data = [trace]
    # Layout
    ymax_ = g_e['value'].max()
    layout = go.Layout(hovermode = 'closest',
                       legend={'orientation':'h'},
                       yaxis = {'range': [0, ymax_*1.1], 'tickformat': ',d'},
                       xaxis = {'title': 'Date', 'showgrid': False},
                       title = go.layout.Title(text = '<Employment>', 
                                               xref = 'paper'))
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


#########################
### LAU - Unmployment ###
#########################
@app.callback(Output('g_un', 'figure'), [Input('id_stat2', 'value')])
def update_output(val):
    df1 = df_lau[(df_lau['state_nm']==val) & (df_lau['time'] >= "2018")]
    g_u = df1[df1['type']=='Unemployment']
    # Data
    trace = go.Scatter(x = g_u['time'],
                       y = g_u['value'],
                       mode = 'lines',
                       name = 'Unemployment')        
    data = [trace]
    # Layout
    ymax_ = g_u['value'].max()
    layout = go.Layout(hovermode = 'closest',
                       legend={'orientation':'h'},
                       yaxis = {'range': [0, ymax_*1.1], 'tickformat': ',d'},
                       xaxis = {'title': 'Date', 'showgrid': False},
                       title = go.layout.Title(text = '<Unemployment>', 
                                               xref = 'paper'))
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


##############################
### LAU - Unmployment Rate ###
##############################
@app.callback(Output('g_r', 'figure'), [Input('id_stat2', 'value')])
def update_output(val):
    df1 = df_lau[(df_lau['state_nm']==val) & (df_lau['time'] >= "2018")]
    g_r = df1[df1['type']=='Rate']
    # define graph data
    trace = go.Scatter(x = g_r['time'],
                       y = g_r['value'],
                       mode = 'lines',
                       name = 'Employment')        
    data = [trace]

    # define graph layout
    ymax_ = g_r['value'].max()
    layout = go.Layout(
        hovermode = 'closest',
        legend={'orientation':'h'},
        yaxis = {'range': [0, ymax_*1.1], 'tickformat': ',d'},
        xaxis = {'title': 'Date', 'showgrid': False},
        title = go.layout.Title(text = '<Unemployment Rate>', 
                                xref = 'paper'))
    # define figure
    figure = {'data': data, 'layout': layout}
    return figure


######################
### BEA - Real GDP ###
######################
@app.callback(Output('bar_gdp', 'figure'), [Input('id_index', 'value')])

def update_output(val):
    df = df_gdp2[df_gdp2['LineDescription'] == val]
    ymax = df['Value'].max()
    ymin = df['Value'].min()
    # Data
    trace = go.Bar(x = df['Time'],
                   y = df['Value'],
                   text = df['Value'],
                   textposition = 'outside')
    data = [trace]
    # Layout
    layout = go.Layout(yaxis = {'title' : 'Real GDP(%)', 'range': [ymin*1.5, ymax*1.5]},
                       height=500,
                       title = go.layout.Title(text = 'Real GDP: Percent change from preceding quarter', 
                                               xref = 'paper'))
    # Figure
    figure = {'data': data, 'layout': layout}
    return figure


# In[70]:


# debug=True는 .py로 실행시킬때 / 주피터 내부에서 실행시키려면 False
if __name__=='__main__':
    app.run_server(debug=False)


# In[ ]:





# In[ ]:




