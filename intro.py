import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])

# Load data
df = pd.read_csv("save_the_bees.csv")

app.layout = html.Div([
html.H1("Bees Population Visualization", style={
        'text-align': 'center',
        'background': 'linear-gradient(to right, #FFD700, #FF8C00)',
        'WebkitBackgroundClip': 'text',
        'color': 'transparent',
        'fontSize': '48px',
        'fontWeight': 'bold',
    }),
   # Year Slider
    dcc.Slider(
        id="slct-year",
        min=2015,
        max=2022,
        step=1,
        value=2015,
        marks={str(year): str(year) for year in range(2015, 2023)},
        tooltip={"placement": "bottom", "always_visible": True},
    ),
    html.Br(),

    dcc.Dropdown(
        id="slct-state",
        options=[{"label": state, "value": state} for state in df["state"].unique()],
        multi=True,
        value=None,
        style={
            'width': "40%",
            'color': 'black',  
        },        
        placeholder="Select State(s)"
    ),
    html.Br(),


    html.Div(id='output_container', children=[]),


    dcc.Tabs([
        dcc.Tab(label='Bee Population Map', children=[
            dcc.Graph(id="bee_map", figure={})
        ],style={'backgroundColor': '#FFA500', 'color': 'black'}),
        dcc.Tab(label='Colony Loss Over Time', children=[
            dcc.Graph(id="colony_loss_time", figure={})
        ],style={'backgroundColor': '#FFA500', 'color': 'black'}),
        dcc.Tab(label='Causes of Colony Loss', children=[
            dcc.Graph(id="loss_causes_bar", figure={})
        ],style={'backgroundColor': '#FFA500', 'color': 'black'}),
    ],
    style={
            'color': 'black', 
            'background-color' : '#FFD700'
        } )
])

@app.callback(
    [Output('output_container', 'children'),
     Output('bee_map', 'figure'),
     Output('colony_loss_time', 'figure'),
     Output('loss_causes_bar', 'figure')],
    [Input('slct-year', 'value'),
     Input('slct-state', 'value')]
)
def update_graphs(selected_year, selected_states):
    # Message for the selected year
    container = f"The year chosen was: {selected_year}"

    numeric_cols = ['varroa_mites', 'other_pests_and_parasites', 'diseases', 'pesticides', 'other', 'unknown']

    # Filter the data for the selected year
    dff = df[df["year"] == selected_year]

    # Default titles
    map_title = "Bee Population in All States"
    time_title = "Total Colony Loss Over Time"
    causes_title = "Average Causes of Colony Loss in All States"
    
    # 1. Choropleth Map of Bee Population by State
    if selected_states:
        # Filter for selected states, then group by state to get the average colonies for each
        dff_map = dff[dff["state"].isin(selected_states)].groupby(['state', 'state_code']).agg({'num_colonies': 'mean'}).reset_index()
    else:
        # Group by state to get the average colonies for each state in the selected year
        dff_map = dff.groupby(['state', 'state_code']).agg({'num_colonies': 'mean'}).reset_index()
    
    bee_map_fig = px.choropleth(
        data_frame=dff_map,
        locationmode='USA-states',
        locations='state_code',
        scope="usa",
        color='num_colonies',
        hover_data={'state': True, 'num_colonies': ':.2f'},
        color_continuous_scale=px.colors.sequential.YlGn,
        labels={'num_colonies': 'Average Number of Bee Colonies'},
        title=map_title,
        template='plotly_dark'
    )
      # 2. Line Chart for Colony Loss Over Time
    if selected_states:
        # Average colony loss for each state and year if multiple entries exist
        dff_time = df[df["state"].isin(selected_states)].groupby(['state', 'year'])['lost_colonies'].mean().reset_index()
        
        time_fig = px.line(
            dff_time,
            x='year',
            y='lost_colonies',
            color='state',
            title=time_title,
            labels={'lost_colonies': 'Average Lost Colonies'},
            template='plotly_dark'
        )
    else:
        # Average colony loss for all states each year
        dff_time = df.groupby("year")['lost_colonies'].mean().reset_index()
        
        time_fig = px.line(
            dff_time,
            x='year',
            y='lost_colonies',
            title=time_title,
            labels={'lost_colonies': 'Average Lost Colonies (All States)'},
            template='plotly_dark'
        )
    # 3. Bar Chart for Causes of Colony Loss
    if selected_states:
        # Group by state and year, calculate the mean of each cause for selected states
        dff_selected = dff[dff["state"].isin(selected_states)].groupby(['state', 'year'])[numeric_cols].mean().reset_index()
        
        # Reshape the data to have 'Cause' and 'Impact Percentage' columns
        dff_causes = dff_selected.melt(id_vars=['state', 'year'], value_vars=numeric_cols, var_name='Cause', value_name='Impact Percentage')
        
        causes_fig = px.bar(
            dff_causes,
            x='Cause',
            y='Impact Percentage',
            color='state',
            barmode='group',
            title=causes_title,
            labels={'Impact Percentage': 'Impact Percentage', 'Cause': 'Cause'},
            template='plotly_dark'
        )
    else:
        # Calculate the mean impact for each cause across all states for the selected year
        dff_all_states = dff.groupby("year")[numeric_cols].mean().reset_index()
        dff_all_states = dff_all_states[dff_all_states["year"] == selected_year]
        
        dff_causes = dff_all_states.melt(id_vars=['year'], value_vars=numeric_cols)
        dff_causes.columns = ['Year', 'Cause', 'Impact Percentage']
        
        causes_fig = px.bar(
            dff_causes,
            x='Cause',
            y='Impact Percentage',
            color_discrete_sequence=['#FFA15A'],
            title=causes_title,
            labels={'Impact Percentage': 'Average Impact Percentage', 'Cause': 'Cause'},
            template='plotly_dark'
        )


    return container, bee_map_fig, time_fig, causes_fig

if __name__ == '__main__':
    app.run_server(debug=True)
