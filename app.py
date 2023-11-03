'''
 # @ Create Time: 2023-11-02 14:37:54.140092
'''
import pickle 
from dash import Dash, html, dcc, Input, Output, dash_table 
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


file_path = 'industry_models.json'#'/Users/iankaplan/Desktop/industry_models.json'

with open(file_path, "rb") as pickle_file:
    industry_models = pickle.load(pickle_file)

file_path = 'industry_correlations.json'#'/Users/iankaplan/Desktop/industry_correlations.json'

with open(file_path, "rb") as pickle_file:
    industry_correlations = pickle.load(pickle_file)

slider_steps = []

for i in range(2015, 2024):
    for j in range(1,5):
        if ((i == 2023) & (j > 3)):
            pass
        else:
            slider_steps.append(f'Q{j} {i}')

industry_list = {}

for industry in industry_correlations:
    industry_list[(str(industry[0]) + ' vs ' +  str(industry[1]))] = industry

dummy_df = pd.read_csv('industry_tables.csv')#'/Users/iankaplan/Desktop/industry_tables.csv')

app = Dash()
server = app.server()
    
    
app.layout = html.Div([
    html.H4('Correlation of Stock Prices by Industry'),
    html.P('Select industries:'),
    dcc.Dropdown(
        id='industries',
        #options = industry for industry in industry_correlations
        options = [{'label': industry, 'value': industry} for industry in industry_list],
        #options=[{'label': f'{industry[0]} vs {industry[1]}', 'value': industry} for industry in industry_correlations],
        value = 'Communication Services vs Consumer Discretionary',
        #persistence = True,
        #persistence_type = 'session',
    ),
    dcc.Graph(id='time-series-chart'),
    dcc.Slider(
        min = 0,
        max = len(slider_steps) - 1,
        step = 1, 
        value = 0,
        tooltip = {'placement': 'bottom', 'always_visible': True},
        updatemode = 'mouseup',
        marks={i: str(slider_steps[i]) for i in range(len(slider_steps)) if i % 2 == 0},
        id = 'slider'
    ),
])

@app.callback(
    Output('time-series-chart', 'figure'),
    Input('industries', 'value'),
    Input('slider', 'value'),
)

def update_graph(industries, timeline):
    #time_slot = 'Q3 2018' 
    time_slot = slider_steps[timeline]
    industries = industry_list[industries]
    industries = (tuple(industries))
    #key = industries
    temp_df = dummy_df
    temp_df['Correlation'] = industry_correlations[industries]
    temp_df  = temp_df.drop(columns={'Perc_Dif'})


    predictions = industry_models[industries][1][slider_steps.index(time_slot)]
    temp_df['Predictions'] = temp_df['Correlation'].iloc[:-len(predictions)].tolist() + predictions.tolist()

    first_non_equal_row = (temp_df['Correlation'] != temp_df['Predictions']).idxmax()
    temp_df = temp_df.iloc[max(first_non_equal_row - 120, 0):first_non_equal_row + 60]


    fig = px.line(temp_df, x='Date', y='Correlation', labels={'date': 'Date', 'Correlation': 'Correlations'})

    fig.add_scatter(x=temp_df['Date'], y=temp_df['Predictions'], mode='lines', line=dict(color='red', dash='dash'), name='Prediction')
    fig.add_scatter(x=temp_df['Date'], y=temp_df['Correlation'], mode='lines', line=dict(color='blue'), name='Correlation')

    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=0), showlegend=True, name=f'Mean Absolute Percentile Error: {industry_models[industries][3][slider_steps.index(time_slot)]:.2%}'))
    #fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=0), showlegend=True, name=f'MSE: {industry_models[industries][2][slider_steps.index(time_slot)]:.2f}'))


    return fig


app.run_server()
