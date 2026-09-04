from dash import Dash, html, dcc, Input, Output
import dash_daq as daq
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# create dash app
app = Dash()

# store path to the csv file
path = 'data/btcusd_1-min_data.csv'

# store csv file in a pandas dataframe
df = pd.read_csv(path)

# convert the default unix timestamps into standard format
df['datetime'] = pd.to_datetime(df['Timestamp'], unit='s')
df = df.dropna()

# create index on datetime so the df can be resampled by this column
df = df.set_index('datetime')

# create a dictonary so the ranges get passed into the config dynamicly 
RANGE_CONFIG = {
    "3H":  {"offset": pd.Timedelta(hours=3),   "resample": "1min"},
    "1T":  {"offset": pd.Timedelta(days=1),     "resample": "5min"},
    "1W":  {"offset": pd.Timedelta(weeks=1),    "resample": "1h"},
    "1M":  {"offset": pd.Timedelta(days=30),    "resample": "4h"},
    "1Y":  {"offset": pd.Timedelta(days=365),   "resample": "D"},
    "Max": {"offset": None,                     "resample": "W"},
}

# app callback on the chart, so the selection of the radio buttons really take place
@app.callback(
    Output('Bitcoin-graph', 'figure'),
    Output('price-diff', 'children'),
    Input('range-selector', 'value'),
    Input('candle-view', 'on'),
)
def update_chart(selected_range, selcted_mode):
    # stores the selectaed range, offset & resample in config
    config = RANGE_CONFIG[selected_range]

    # gets the last timestamp
    last_timestamp = df.index.max()

    # selects the data from the last timestamp minus the selected time
    if config["offset"] is None:
        filtered_df = df
    else:
        start = last_timestamp - config["offset"]
        filtered_df = df[df.index >= start]

    #dynamic resampling regarding to the selected time frame
    resampled_df = filtered_df.resample(config["resample"]).agg({
        'Open':  'first',
        'High':  'max',
        'Low':   'min',
        'Close': 'last'
    }).dropna()

    if selcted_mode == bool(0):
        fig = px.line(resampled_df, x=resampled_df.index, y='High',
                    hover_data=['Open', 'Low', 'Close']
        )
        
        fig.update_layout(
        title='Line Chart',
        yaxis=dict(tickformat='$,.0f')
        )

        fig.update_traces(
            hovertemplate='High: $%{y:,.0f}<br>Open: $%{customdata[0]:,.0f}<br>Low: $%{customdata[1]:,.0f}<br>Close: $%{customdata[2]:,.0f}'
        )
    else:
        fig = go.Figure(data=[go.Candlestick(
        x=resampled_df.index,   # x-achses = datetime
        open=resampled_df['Open'],   # open price
        high=resampled_df['High'],   # highest price
        low=resampled_df['Low'],     # lowest price
        close=resampled_df['Close']  # close price
        )])

        fig.update_layout(
        title='Candlestick Chart',
        xaxis_title='Datum',
        yaxis_title='Preis',
        xaxis_rangeslider_visible=False 
        )


    # To calculate percentage between start index end end index
    start_price = resampled_df['Close'].iloc[0]
    end_price = resampled_df['Close'].iloc[-1]

    diff = end_price - start_price
    diff_pct = (diff / start_price) * 100

    # add symbols and color to the diffrence
    direction = "▲" if diff >= 0 else "▼"
    color = "green" if diff >= 0 else "red"

    # show diff on dashboard
    diff_text = html.Span(
        f"{direction} ${diff:,.0f} ({diff_pct:.2f}%)",
        style={"color": color, "fontWeight": "bold", "fontSize": "18px"}
    )

    return fig, diff_text


app.layout = html.Div(children=[
    html.H1(children='Bitcoin Dashboard'),

    html.Div(children='''
        This dashboard visualizes the historical Bitcoin price in Dollar.
    '''),

    html.Br(),

     dcc.RadioItems(
        id='range-selector',
        options=[
            {"label": "3H",  "value": "3H"},
            {"label": "1D",  "value": "1D"},
            {"label": "1W",  "value": "1W"},
            {"label": "1M",  "value": "1M"},
            {"label": "1Y",  "value": "1Y"},
            {"label": "Max", "value": "Max"},
        ],
        value="Max",  # Default
        inline=True  
    ),

    html.Br(),

    html.Div(
    daq.BooleanSwitch(
        id='candle-view',
        on=False,
        label="Candle view",
        labelPosition="top",
    ),
    style={
        'display': 'flex',
        'justifyContent': 'flex-start',  
        'alignItems': 'center',
        'width': '100%'
        }
    ),

    html.Br(),

    html.Div(id='price-diff'),

    dcc.Graph(
        id='Bitcoin-graph'
    )
])

if __name__ == '__main__':
    app.run(debug=True)

