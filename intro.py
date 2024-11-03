import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

df = pd.read_csv("save_the_bees.csv")
print(df[:5])

app.layout = html.Div([
    html.H1("Bees Population Visualization", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct-year",
                 options=[
                     {"label": "2015", "value": 2015},
                     {"label": "2016", "value": 2016},
                     {"label": "2017", "value": 2017},
                     {"label": "2018", "value": 2018},
                     {"label": "2019", "value": 2019},
                     {"label": "2020", "value": 2020},
                     {"label": "2021", "value": 2021},
                     {"label": "2022", "value": 2022}],
                     multi=False,
                     value=2015,
                     style={'width': "40%"}
                     ),
    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id="my_bee_map", figure={})
])

@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct-year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "The year chosen was: {}".format(option_slctd)

    dff = df.copy()
    dff = dff[dff["year"] == option_slctd]

    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state_code',
        scope="usa",
        color='num_colonies',
        hover_data=['state','num_colonies'],
        color_continuous_scale=px.colors.sequential.YlGn,
        labels={'num_colonies': 'Number of Bee Colonies'},
        template='plotly_dark'
    )

    return container,fig

if __name__ == '__main__':
    app.run_server(debug=True)
