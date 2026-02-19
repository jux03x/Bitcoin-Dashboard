# Bitcoin Candlestick Chart Dashboard

An interactive Bitcoin price visualization dashboard built with Python, Plotly, and Dash — designed to be hosted locally or on a home server.

---

## Project Goals

This project is structured in three sequential steps:

**Step 1 – Visualization:** Load the Kaggle *Bitcoin Historical Data* dataset locally and display it as an interactive candlestick chart with time-range selectors, hover tooltips, and a volume panel.

**Step 2 – Automated Data Updates:** Keep the dataset current without manual intervention, either via the Kaggle API or by pulling new OHLCV data directly from the Bitstamp REST API and appending it to the local CSV.

**Step 3 – Forecasting *(planned)*:** Apply statistical or machine learning methods to historical price data to generate a price forecast and visualize it alongside the historical chart.

---

## Tech Stack & Dependency Rationale

| Package | Purpose | Why this choice |
|---|---|---|
| `pandas` | Data loading, cleaning, resampling | The standard for time-series DataFrames in Python |
| `plotly` | Candlestick chart rendering | Native `Candlestick` chart type, built-in hover tooltips, range selectors, and smooth interactivity — far better suited for financial charts than Seaborn (static) or Altair (complex for OHLC) |
| `dash` | Web application framework | Built on top of Plotly and Flask — no extra translation layer needed between the chart and the UI. Enables dropdowns, callbacks, and live updates with minimal code |
| `flask` | Underlying web server (via Dash) | Dash runs on Flask, so using Dash already gives you a Flask server — suitable for local use and home server deployment |
| `requests` | HTTP calls to Bitstamp API | Lightweight, standard Python HTTP library for Step 2 |
| `python-dotenv` | Environment variable management | Keeps API credentials out of source code and the public repository |

### Install all dependencies

```bash
pip install pandas plotly dash requests python-dotenv
```

---

## Project Structure

```
bitcoin-dashboard/
│
├── data/
│   └── btcusd_1-min_data.csv        # The Kaggle dataset (not committed to git)
│
├── app.py                            # Step 1: Main Dash application
├── updater.py                        # Step 2: Data update script
├── forecaster.py                     # Step 3: Forecasting module (planned)
│
├── .env                              # API credentials — NOT committed to git
├── .gitignore
└── README.md
```

**Important:** Add the following to your `.gitignore` to make sure sensitive files and large data files are never pushed to a public repository:

```
.env
data/
__pycache__/
*.pyc
```

---

## Step 1 — Interactive Candlestick Chart

The goal of this step is to read the downloaded CSV file, process the data, and display a fully interactive candlestick chart inside a Dash web application running locally in your browser.

### 1.1 — Load and Clean the Dataset

Open the CSV file using `pandas`. The dataset contains the columns `Timestamp` (Unix time), `Open`, `High`, `Low`, `Close`, and `Volume`. Convert the Unix `Timestamp` column into proper Python `datetime` objects so that Plotly can interpret the time axis correctly. Drop any rows where the OHLC values are missing, as these would break the chart rendering, and sort the DataFrame by date in ascending order.

### 1.2 — Resample to a Meaningful Granularity

The dataset contains one-minute candles, which means millions of rows for multi-year data. Rendering all of them at once would be slow and visually unreadable. Use `pandas` resampling to aggregate the one-minute data into daily candles. For each day, the `Open` is the first value of the day, `High` is the maximum, `Low` is the minimum, `Close` is the last value, and `Volume` is the sum of all minute-volumes for that day.

### 1.3 — Build the Candlestick Chart with Plotly

Use Plotly's `make_subplots` to create a chart with two panels sharing the same X axis: a large upper panel for the candlestick chart (roughly 75% of the height) and a smaller lower panel for the trading volume bars (roughly 25%). Add a `go.Candlestick` trace to the upper panel, passing the date index and the Open, High, Low, Close columns. Color rising candles green and falling candles red. Add a `go.Bar` trace to the lower panel for volume, with matching green/red coloring per bar depending on whether the close was higher or lower than the open on that day.

### 1.4 — Configure Interactivity

In the chart layout, add a `rangeselector` to the X axis with preset buttons for common time ranges: 1 month, 3 months, 6 months, 1 year, 3 years, and "Max" to show all available data. Add a `rangeslider` beneath the volume panel so the user can drag to select any custom time window. Set `hovermode` to `"x unified"` so that hovering over any point on the chart shows a single tooltip with all OHLCV values for that date simultaneously. Apply a dark theme using Plotly's `plotly_dark` template for a clean, professional look.

### 1.5 — Wrap Everything in a Dash Application

Create a `Dash` app instance and define a simple layout that contains the Plotly chart as a `dcc.Graph` component filling the full browser viewport. Add a `dcc.Dropdown` above the chart that lets the user switch between chart granularities (e.g., Daily, Weekly, Monthly). Wire up a Dash `@callback` that listens to the dropdown selection, re-aggregates the DataFrame using the chosen time interval, rebuilds the Plotly figure, and returns it to the `dcc.Graph` component. This callback pattern is the core of Dash interactivity and makes the chart respond to user input without any page reload.

### 1.6 — Run the Application

At the bottom of `app.py`, start the Dash development server with `app.run(debug=True)`. Open your browser and navigate to `http://localhost:8050` to see the running dashboard. For home server deployment, change the host to `0.0.0.0` so the app is accessible from other devices on your local network.

---

## Step 2 — Automated Data Updates

> *Detailed implementation coming in the next project phase.*

This step will cover two approaches to keeping the dataset current:

**Option A — Kaggle API:** Automatically re-download the full dataset daily using the `kaggle` Python package and API credentials stored securely in a `.env` file (never committed to git). On platforms like GitHub Actions, credentials will be stored as repository secrets.

**Option B — Bitstamp Direct Feed (recommended):** After the initial Kaggle download, use the free Bitstamp REST API to fetch only the latest OHLCV candles and append them to the existing local CSV. This approach is independent of third-party upload schedules and keeps the data fresher. A scheduler (cron on Linux/macOS, Task Scheduler on Windows) will trigger the update script daily.

This step will also include a mechanism to trigger a chart data reload after an update completes, so the Dash app reflects the latest data without manual intervention.

---

## Step 3 — Price Forecasting

> *Planned for a future project phase.*

This step will add a forecasting layer on top of the historical data. Candidate approaches include:

- **Facebook Prophet** — a time-series forecasting library designed for data with seasonal patterns; delivers confidence intervals and integrates cleanly with Plotly for visualization
- **ARIMA / SARIMA** — classical statistical models from the `statsmodels` library, suitable for short-term trend extrapolation
- **LSTM Neural Networks** — deep learning approach via TensorFlow/Keras for sequence modeling

The forecast will be rendered as an additional trace on the existing candlestick chart, visually distinguished from the historical data with a different color and a shaded confidence band.

---

## Security Notes

- **Never commit your `.env` file.** It contains your Kaggle API key and any other credentials.
- Store secrets in environment variables locally via `.env` + `python-dotenv`.
- For public CI/CD pipelines (e.g., GitHub Actions), use repository secrets configured in the GitHub web interface under *Settings → Secrets and variables → Actions*.
- The `data/` directory is excluded from git because the CSV file is large and contains no secrets — it can always be re-downloaded.
