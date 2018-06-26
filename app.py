import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s==%(funcName)s==%(message)s')

health_df = pd.read_csv('data/country_data_master.csv',
                        usecols=['country', 'lon', 'lat', 'population', 
                                 'map_ref', 'gdp', 'health_exp_perc'])
health_df['health_industry_usd'] = health_df['health_exp_perc'].mul(health_df['gdp']).div(100)

app = dash.Dash()
app.title = 'Health Expenditure per Country - 2017'
server = app.server 

app.layout = html.Div([
    dcc.Graph(id='country_scatter',
              config={'displayModeBar': False}),
    html.Div([
        html.Div([
            dcc.Dropdown(id='abs_perc',
                 options=[{'label': 'Percent Healthcare Spending', 'value': 'health_exp_perc'},
                            {'label': 'Healthcare Insustry Size $US', 'value': 'health_industry_usd'}],
                 value='health_exp_perc'),

            ], style={'width': '25%', 'display': 'inline-block'}),
    
        html.Div([
            dcc.RangeSlider(id='perc_slider',
                            pushable=True,
                            updatemode='drag',
                            marks={k: {'label': str(k)+'%'} 
                                   for k in range(1, 19)},
                            min=1,
                            max=18,
                            step=1,
                            dots=True,
                            value=[12, 18]),
            html.Br(), html.Br(), html.Br(), html.Br(),

        ], style={'width': '70%', 
                  'float': 'right', 
                  'display': 'inline-block',
                  }),
    ], style={'width': '70%', 'margin-left': '15%'}),

    html.A('@eliasdabbas', href='https://www.twitter.com/eliasdabbas'), 
    html.P(),
    html.Content('Data: CIA World Factobook  '),
    html.A('Health Expenditure', href='https://www.cia.gov/library/publications/the-world-factbook/fields/2225.html'),
    html.Br(),
    html.Content('  Code: '),
    html.A('github.com/eliasdabbas/health_spending', href='https://github.com/eliasdabbas/health_spending'), html.Br(), html.Br(),
    html.Content('This entry provides the total expenditure on health as a percentage of GDP. Health expenditures are '
                 'broadly defined as activities performed either by institutions or individuals through the application '
                 'of medical, paramedical, and/or nursing knowledge and technology, the primary purpose of which is to '
                 'promote, restore, or maintain health.')

], style={'background-color': '#eeeeee'})


@app.callback(Output('perc_slider', 'marks'),
             [Input('abs_perc', 'value')])
def set_marks(numtype):
    if numtype == 'health_exp_perc':
        return {k: {'label': str(k)+'%'} for k in range(1, 19)}
    if numtype == 'health_industry_usd':
        return {k: {'label': lab} for k, lab in 
                zip(range(6, 14), ['$1M', '$10M', '$100M', '$1B', '$10B', '$100B', '$1T', '$10T'])}
    
@app.callback(Output('perc_slider', 'min'),
             [Input('abs_perc', 'value')])
def set_minimum(numtype):
    return 1 if numtype == 'health_exp_perc' else 6

@app.callback(Output('perc_slider', 'max'),
             [Input('abs_perc', 'value')])
def set_maximum(numtype):
    return 18 if numtype == 'health_exp_perc' else 13

@app.callback(Output('country_scatter', 'figure'),
             [Input('perc_slider', 'value'), Input('abs_perc', 'value')])
def write_numbers(numbers, abs_perc):
    logging.info(msg=locals())
    col = 'health_exp_perc' if abs_perc == 'health_exp_perc' else 'health_industry_usd'
    numbers = numbers if abs_perc == 'health_exp_perc' else [10**x for x in numbers]
    df = health_df[health_df[col].between(numbers[0], numbers[1])]
    df = df.sort_values([col])
    return {
        'data': [go.Scattergeo(lon=df['lon'],
                               lat=df['lat'],
                               mode='markers',
                               marker={'color': df[col],
                                       'size': 22,
                                       'opacity': 0.85,
                                       'showscale': True,
                                       'colorscale': 'Cividis',
                                       'colorbar': {'ticksuffix': '%' if col == 'health_exp_perc' else '',
                                                    'tickprefix': '' if col == 'health_exp_perc' else '$',
                                                    'outlinewidth': 0, 
                                                    'title': '%' if abs_perc == 'health_exp_perc' else 'US$ est.'
                                                    }},
                               hoverinfo='text',
                               hovertext='<b>'+ df['country'] +'</b>' + '<br>' + '<br>' +
                                    'Percent of GDP: ' + df['health_exp_perc'].astype(str) + '%'+ '<br>' +
                                    'Estimated Industry Size: $' + [f'{x:,.0f}' for x in df['health_industry_usd']]
                               )],
        'layout': go.Layout(title='<b>' + '% Spent on Healthcare' + '</b>'+ '<br>' +
                                  'Countries spending ' + ' - '.join([str(numbers[0])+'%', str(numbers[1])+'%']) +
                                  ' of GDP on Healthcare'
                                  if abs_perc == 'health_exp_perc' else
                                  '<b>' + 'Estimated Healthcare Industry Size' '</b>'+ '<br>' +
                                  'Countries spending ' + ' - '.join(['$'+ str(f'{numbers[0]:,}'), '$'+str(f'{numbers[1]:,}')]) +
                                  ' on Healthcare',
                            height=600,
                            annotations=[{'text': '<a href="https://www.twitter.com">@eliasdabbas</a>', 'x': .2, 'y': .1, 
                                          'showarrow': False},
                                         {'text': 'Data: CIA World Factbook', 'x': .2, 'y': .07, 'showarrow': False}],
                            font={'family': 'Palatino'},
                            margin={'r': 10, 'l': 30, 'b': 30, 't': 70},
                            plot_bgcolor='#eeeeee',
                            paper_bgcolor='#eeeeee',
                            geo={'showland': True, 'landcolor': '#eeeeee',
                                 'countrycolor': '#cccccc',
                                 'showcountries': True,
                                 'oceancolor': '#eeeeee',
                                 'showocean': True,
                                 'showcoastlines': True,
                                 'coastlinecolor': '#cccccc',
                                 'showframe': False,
                               },
                            ),
        
    }

if __name__ == '__main__':
    app.run_server()