# Soon to be transfered into a Candle Chart
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

app = Dash()

path = 'data/btcusd_1-min_data.csv'

df = pd.read_csv(path)

df['datetime'] = pd.to_datetime(df['Timestamp'], unit='s')
df = df.dropna()
df = df.set_index('datetime')
RANGE_CONFIG = {
    "3H":  {"offset": pd.Timedelta(hours=3),   "resample": "1min"},
    "1T":  {"offset": pd.Timedelta(days=1),     "resample": "5min"},
    "1W":  {"offset": pd.Timedelta(weeks=1),    "resample": "1h"},
    "1M":  {"offset": pd.Timedelta(days=30),    "resample": "4h"},
    "1Y":  {"offset": pd.Timedelta(days=365),   "resample": "D"},
    "Max": {"offset": None,                     "resample": "W"},
}

@app.callback(
    Output('Bitcoin-graph', 'figure'),
    Output('price-diff', 'children'),
    Input('range-selector', 'value')
)
def update_chart(selected_range):
    config = RANGE_CONFIG[selected_range]

    
    last_timestamp = df.index.max()

    if config["offset"] is None:
        filtered_df = df
    else:
        start = last_timestamp - config["offset"]
        filtered_df = df[df.index >= start]

    resampled_df = filtered_df.resample(config["resample"]).agg({
        'Open':  'first',
        'High':  'max',
        'Low':   'min',
        'Close': 'last'
    }).dropna()

    fig = px.line(resampled_df, x=resampled_df.index, y='High',
                  hover_data=['Open', 'Low', 'Close'])

    fig.update_layout(yaxis=dict(tickformat='$,.0f'))
    fig.update_traces(
        hovertemplate='High: $%{y:,.0f}<br>Open: $%{customdata[0]:,.0f}<br>Low: $%{customdata[1]:,.0f}<br>Close: $%{customdata[2]:,.0f}'
    )

    start_price = resampled_df['Close'].iloc[0]
    end_price = resampled_df['Close'].iloc[-1]

    diff = end_price - start_price
    diff_pct = (diff / start_price) * 100

    direction = "▲" if diff >= 0 else "▼"
    color = "green" if diff >= 0 else "red"

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

     dcc.RadioItems(
        id='range-selector',
        options=[
            {"label": "3H",  "value": "3H"},
            {"label": "1T",  "value": "1T"},
            {"label": "1W",  "value": "1W"},
            {"label": "1M",  "value": "1M"},
            {"label": "1Y",  "value": "1Y"},
            {"label": "Max", "value": "Max"},
        ],
        value="Max",  # Default
        inline=True  
    ),

    html.Div(id='price-diff'),

    dcc.Graph(
        id='Bitcoin-graph'
    )
])

if __name__ == '__main__':
    app.run(debug=True)

