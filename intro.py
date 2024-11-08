import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])

# Load data
df = pd.read_csv("save_the_bees.csv")

quarter_to_season = {
    1: 'Winter (Jan-Mar)',
    2: 'Spring (Apr-Jun)',
    3: 'Summer (Jul-Sep)',
    4: 'Fall (Oct-Dec)'
}

app.layout = html.Div([
    html.Div([
          # Bee Image next to the title (smaller size)
        html.Div(
            children=[html.Img(id='bee_image', src='assets/bee.png', className='happy-bee')],
            style={
                'display': 'inline-block',  # Make sure it sits next to the title
                'verticalAlign': 'middle',  # Align vertically with the title
            }
        ),
        html.H1("Bees Population Visualization", style={
            'text-align': 'center',
            'background': 'linear-gradient(to right, #FFD700, #FF8C00)',
            'WebkitBackgroundClip': 'text',
            'color': 'transparent',
            'fontSize': '48px',
            'fontWeight': 'bold',
            'flex': '1',  # Take up the available space
            'display': 'inline-block',
            'margin': '0',
        }),

      
    ], style={
        'display': 'flex',  # Use flexbox to align the items horizontally
        'justifyContent': 'center',  # Center horizontally
        'alignItems': 'center',  # Align vertically
        'marginBottom': '20px'  # Some space below the title + bee
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
            dcc.Graph(id="bee_map", figure={},style={'height': '600px', 'width': '100%'})
        ],style={'backgroundColor': '#FFA500', 'color': 'black'}),
        dcc.Tab(label='Colony Loss for different Seasons', children=[
                dcc.Graph(id="loss_by_quarter", figure={}),
        ],style={'backgroundColor': '#FFA500', 'color': 'black'}),
        dcc.Tab(label='Causes of Colony Loss', children=[
            dcc.Graph(id="loss_causes_bar", figure={})
        ],style={'backgroundColor': '#FFA500', 'color': 'black'}),
    ],
    style={
            'color': 'black', 
            'background-color' : '#FFD700'
        } ),

    dcc.Graph(id="colony_loss_time", figure={}),
    # dcc.Graph(id="renovation_by_quarter", figure={}),
    # dcc.Graph(id="total_vs_max_colonies", figure={}),
    # dcc.Graph(id="percent_lost_vs_renovated", figure={})
])

@app.callback(
    [Output('output_container', 'children'),
     Output('bee_map', 'figure'),
     Output('colony_loss_time', 'figure'),
     Output('loss_causes_bar', 'figure'),
     Output('loss_by_quarter', 'figure')],
    [Input('slct-year', 'value'),
     Input('slct-state', 'value')]
)
def update_graphs(selected_year, selected_states):
    # Message for the selected year
    container = f"The year chosen was: {selected_year}"

    numeric_cols = ['varroa_mites', 'other_pests_and_parasites', 'diseases', 'pesticides', 'other', 'unknown']

    # Calculate the yearly average for `num_colonies` for each state
    df_avg = df.groupby(['state', 'state_code', 'year'])['num_colonies'].mean().reset_index()


    # Filter the data for the selected year
    dff = df_avg[df_avg["year"] == selected_year]

    # Default titles
    map_title = "Average Bee Population by State (Yearly)"
    time_title = "Total Colony Loss Over Time"
    causes_title = f"Average Causes of Colony Loss in {selected_year}"

    # 1. Choropleth Map of Bee Population by State
    if selected_states:
        # Filter for selected states
        dff_map = dff[dff["state"].isin(selected_states)]
    else:
        dff_map = dff

    bee_map_fig = px.choropleth(
        data_frame=dff_map,
        locationmode='USA-states',
        locations='state_code',
        scope="usa",
        color='num_colonies',
        hover_data={'state': True, 'num_colonies': ':.2f'},
        color_continuous_scale=px.colors.sequential.algae,  
        range_color=[dff_map['num_colonies'].min(), dff_map['num_colonies'].max()],  
        labels={'num_colonies': 'Avg Number of Bee Colonies'},
        title=map_title,
        template='plotly_dark'
    )

    # 2. Line Chart for Colony Loss Over Time
    if selected_states:
        dff_time = df[df["state"].isin(selected_states)].groupby(['state', 'year'])['lost_colonies'].mean().reset_index()

        time_fig = px.line(
            dff_time,
            x='year',
            y='lost_colonies',
            color='state',
            title=time_title,
            labels={'lost_colonies': 'Avg Lost Colonies'},
            template='plotly_dark'
        )
    else:
        dff_time = df.groupby("year")['lost_colonies'].mean().reset_index()

        time_fig = px.line(
            dff_time,
            x='year',
            y='lost_colonies',
            title=time_title,
            labels={'lost_colonies': 'Avg Lost Colonies (All States)'},
            template='plotly_dark'
        )

    # 3. Bar Chart for Causes of Colony Loss (Grouped by State)
    if selected_states:
        # Filter for selected states and year, then calculate the mean for each factor
        dff_selected = df[(df["state"].isin(selected_states)) & (df["year"] == selected_year)]
        dff_causes = dff_selected.groupby(['state', 'year'])[numeric_cols].mean().reset_index()

        # Create a title for the bar chart based on selected states
        causes_title = f"Average Causes of Colony Loss in {', '.join(selected_states)} for {selected_year}"
    else:
        # Calculate the average impact for each cause across all states for the selected year
        dff_selected = df[df["year"] == selected_year]
        dff_causes = dff_selected.groupby('year')[numeric_cols].mean().reset_index()

    # **Ensure that `state` is retained before the `melt` function**
    # This ensures that `state` and `year` columns are present
    if 'state' not in dff_causes.columns:
        # If `state` was dropped, we add it manually by copying it from the original data
        dff_causes['state'] = selected_states[0] if selected_states else 'All States'

    # Reshape the data to have 'Cause' and 'Impact Percentage' columns for plotting
    dff_causes = dff_causes.melt(id_vars=['state', 'year'], value_vars=numeric_cols, var_name='Cause', value_name='Impact Percentage')

    # Plot the Bar Chart (if states are selected, we'll group the bars by state)
    causes_fig = px.bar(
        dff_causes,
        x='Cause',
        y='Impact Percentage',
        color='state',
        barmode='group',
        title=causes_title,
        labels={'Impact Percentage': 'Avg Impact Percentage', 'Cause': 'Cause'},
        template='plotly_dark'
    )
    # 4. Colony Loss by Quarter
    dff2 = df[df["year"] == selected_year]


    if selected_states:
        dff_quarter_loss = dff2[dff2["state"].isin(selected_states)].groupby('quarter')['lost_colonies'].mean().reset_index()
    else:
        dff_quarter_loss = dff2.groupby('quarter')['lost_colonies'].mean().reset_index()

    dff_quarter_loss['season'] = dff_quarter_loss['quarter'].map(quarter_to_season)

    # Create the pie chart
    loss_by_quarter_fig = px.pie(
        dff_quarter_loss,
        names='season',
        values='lost_colonies',
        color='season',
        title=f"Colony Loss by Season in {selected_year}",
        labels={'lost_colonies': 'Avg Lost Colonies'},
        template='plotly_dark'
    )

    return container, bee_map_fig, time_fig, causes_fig, loss_by_quarter_fig



if __name__ == '__main__':
    app.run_server(debug=True)
