import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from dash import callback_context
from dash.exceptions import PreventUpdate

# Load your data and process it
data1 = pd.read_csv('netflix1.csv')
data2 = pd.read_csv('netflix2.csv')

# Initial dataset
current_data = data1

current_data['date_added'] = pd.to_datetime(current_data['date_added'])
current_data['year_added'] = current_data['date_added'].dt.year
current_data['month_added'] = current_data['date_added'].dt.month_name()
current_data['day_added'] = current_data['date_added'].dt.day_name()

types = current_data["type"].value_counts()
given_directors = current_data['director'].value_counts().sum() - current_data['director'].value_counts().iloc[0]
countries = current_data["country"].value_counts()
countries = countries[countries.index != 'Not Given']
movies_added_year = current_data[current_data['type'] == 'Movie'].groupby(current_data["year_added"])["type"].count()
tv_added_year = current_data[current_data['type'] == 'TV Show'].groupby(current_data["year_added"])["type"].count()

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Netflix Data Analysis Dashboard"),

    html.Div([
        dcc.Dropdown(
            id='dataset-dropdown',
            options=[
                {'label': 'Netflix Dataset 1', 'value': 'data1'},
                {'label': 'Netflix Dataset 2', 'value': 'data2'},
            ],
            value='data1',
            style={'width': '50%'}
        ),
    ], style={'width': '100%', 'display': 'inline-block'}),

    html.Div([
        dcc.Dropdown(
            id='graph-type-dropdown',
            options=[
                {'label': 'Select Graph Type', 'value': 'placeholder'},
                {'label': 'Bar Chart - Show Types', 'value': 'bar_chart_show_types'},
                {'label': 'Bar Chart - Top 5 Countries', 'value': 'bar_chart_countries'},
                {'label': 'Pie Chart - Show Categories', 'value': 'pie_chart_categories'},
                {'label': 'Line Chart - Movies Added per Year', 'value': 'line_chart_movies_added_year'},
                {'label': 'Line Chart - TV Shows Added per Year', 'value': 'line_chart_tv_added_year'},
            ],
            value='placeholder',
            style={'width': '50%'}
        ),
    ], style={'width': '100%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(id='graph-output'),
    ], style={'width': '100%', 'display': 'inline-block', 'margin-top': '20px'}),

])

# Callback to update the dataset based on user selection
@app.callback(
    Output('graph-output', 'figure'),
    [Input('dataset-dropdown', 'value'),
     Input('graph-type-dropdown', 'value')]
)
def update_graph(selected_dataset, selected_graph):
    ctx = callback_context
    if not ctx.triggered_id:
        raise PreventUpdate

    if selected_dataset == 'data1':
        current_data = data1
    elif selected_dataset == 'data2':
        current_data = data2
    else:
        raise PreventUpdate

    current_data['date_added'] = pd.to_datetime(current_data['date_added'])
    current_data['year_added'] = current_data['date_added'].dt.year
    current_data['month_added'] = current_data['date_added'].dt.month_name()
    current_data['day_added'] = current_data['date_added'].dt.day_name()

    if selected_graph == 'placeholder':
        # User hasn't made a selection yet, show welcome message
        return go.Figure(data=[go.Scatter(x=[], y=[], text='Welcome to the Netflix Data Analysis Dashboard')],
                         layout=go.Layout(title='Welcome Message'))

    if selected_graph == 'bar_chart_show_types':
        return px.bar(data_frame=current_data["type"].value_counts(), x=current_data["type"].value_counts().index,
                      y=current_data["type"].value_counts(), color=current_data["type"].value_counts().index,
                      color_discrete_sequence=["darkred", "royalblue"],
                      labels={'y': 'Sum', 'type': 'Show Type', 'color': 'Show Type'},
                      title='Bar Chart - Show Types')


    elif selected_graph == 'bar_chart_countries':
        return px.bar(x=countries.head(5).index, y=countries.head(5),
                      color=countries.head(5).index,
                      color_discrete_sequence=px.colors.qualitative.G10,
                      labels={'x': 'Countries', 'y': 'No of shows added', 'color': 'Countries'},
                      title='Bar Chart - Top 5 Countries')

    elif selected_graph == 'pie_chart_categories':
        return go.Figure(data=[go.Pie(labels=current_data["type"].value_counts().index,
                                     values=current_data["type"].value_counts().values)],
                         layout=go.Layout(title='Pie Chart - Show Categories'))

    elif selected_graph == 'line_chart_movies_added_year':
        movies_added_year = current_data[current_data['type'] == 'Movie'].groupby(current_data["year_added"])["type"].count()
        return px.line(x=movies_added_year.index, y=movies_added_year, markers=True, line_shape='spline',
                       width=900, height=500, labels={'x': 'Year', 'y': 'Nº of additions'},
                       title='Line Chart - Movies Added per Year')

    elif selected_graph == 'line_chart_tv_added_year':
        tv_added_year = current_data[current_data['type'] == 'TV Show'].groupby(current_data["year_added"])["type"].count()
        return px.line(x=tv_added_year.index, y=tv_added_year, markers=True, line_shape='spline',
                       width=900, height=500, labels={'x': 'Year', 'y': 'Nº of additions'},
                       title='Line Chart - TV Shows Added per Year')


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
