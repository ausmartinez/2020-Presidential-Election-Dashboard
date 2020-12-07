import pandas as pd
import seaborn as sns
import re
import plotly
import plotly.graph_objects as go
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html


app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)


state_code = pd.read_csv('state-name-code.csv')
state_code.columns = [x.lower() for x in state_code.columns]
raw_data = pd.read_csv('all-state-changes.csv')
raw_data.shape


# Cleaning State column, split electoral votes, convert to datetime
data = raw_data.copy()
ev = []
stateCorrect = []
for i in range(len(data['state'])):
    temp = []
    st = ''
    for char in re.split(' |(|)',data['state'][i]):
        if (str(char).isdigit()):
            temp.append(char)
    ev.append(int(''.join(temp).strip()))
    op = data['state'][i].find('(')
    stateCorrect.append(data['state'][i][:op-1])
data['electoral_votes'] = ev
data['state'] = stateCorrect
data['timestamp'] = pd.DatetimeIndex(pd.to_datetime(data['timestamp'])).to_period('D')


# Daily reporting of leading candidate votes
def figOne():
    years = []
    steps = []
    for i in data['timestamp'].unique():
        temp = data[data['timestamp'] == i]
        aggre = temp.groupby('state').agg({'leading_candidate_votes':'max','trailing_candidate_votes':'max'})
        aggre = aggre.merge(state_code, on='state').reset_index(drop=True)
        tdata = {'type': 'choropleth',
                 'colorscale': 'Greens',
                 'locations': aggre['code'].astype(str),
                 'z': aggre['leading_candidate_votes'].astype(float),
                 'locationmode': 'USA-states'}
        years.append(tdata)
    for i in range(len(years)):
        step = {'method': 'restyle',
                'args': ['visible', [False] * len(years)],
                'label': f'Day {i}'}
        step['args'][1][i] = True
        steps.append(step)
    sliders = [{'active': 0,
                'pad': {"t": 1},
                'steps': steps}]
    layout = dict(geo={'scope': 'usa',
                       'projection': {'type': 'albers usa'}},
                  sliders=sliders)
    return go.Figure(data = years, layout = layout)


app.layout = html.Div([
    html.Div([
        html.H2('Figure 1', className='center'),
        dcc.Graph(figure=figOne(), id = "figure1")
    ])
])


if __name__ == "__main__":
#     app.run_server(mode='inline')
    app.run_server()
