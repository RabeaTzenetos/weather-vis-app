import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import os
import boto3
from io import StringIO
from time import sleep
import threading

from tasks import plot_line

# AWS credentials
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# S3 bucket and file information
bucket_name = "elasticbeanstalk-us-east-2-780026431059"
file_key = "forecast.csv"

# create S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)


def read_csv_from_s3(bucket: str, key: str) -> pd.DataFrame:
    """
    Download csv content from S3 bucket
    """
    try:
        # download CSV content
        response = s3.get_object(Bucket=bucket, Key=key)
        csv_content = response["Body"].read().decode("utf-8")

        df = (
            pd.read_csv(StringIO(csv_content), parse_dates=["date"])
            .drop(columns="Unnamed: 0", errors="ignore")
            .round(1)
        )

        return df
    except Exception as e:
        print(f"Error reading CSV from S3: {e}")
        return None


# load data
df = read_csv_from_s3(bucket_name, file_key)


def update_data(timer: int = 500):
    """
    Use initial df as global variable, update with latest csv data at specified time interval
    """
    global df
    while True:
        # read latest CSV from S3
        latest_df = read_csv_from_s3(bucket_name, file_key)

        # update global df
        if latest_df is not None:
            df = latest_df

        sleep(timer)  # check every X seconds


update_thread = threading.Thread(target=update_data)
update_thread.start()

# make initial plot with default values
initial_fig = plot_line(
    df,
    cities="London",
    temp_threshold=2,
    wind_threshold=10,
    cloud_threshold=40,
)

# initialise app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
application = app.server

# set app layout
app.layout = html.Div(
    children=[
        html.Br(),
        html.H1("Weather Vis", style={"textAlign": "center"}),
        html.Br(),
        html.P(
            """
            Weather forecast for selected cities over the next 7 days.
            Changes from one hour to the next that exceed the selected thresholds are highlighted.
            """,
            style={"margin-left": "20px"},
        ),
        html.Hr(
            style={"border-color": "black", "border-width": "1px", "margin": "20px 0"}
        ),
        html.Br(),
        dcc.Checklist(
            options=[
                {"label": city, "value": city} for city in sorted(df["city"].unique())
            ],
            value=["London"],  # set default value
            id="checkboxes",
            style={
                "width": "50%",
                "margin": "20px",
            },
            labelStyle={
                "display": "inline-block",
                "margin-right": "10px",
            },
            inputStyle={"margin-right": "5px"},  # add margin between checkboxes
            inline=True,  # display checkboxes in a line
        ),
        html.Br(),
        html.Div(
            [
                html.Label("Temperature Threshold (°C)"),
                dcc.Slider(
                    id="temp-slider",
                    min=1,
                    max=10,
                    step=1,
                    value=2,
                    marks={i: str(i) for i in range(1, 11, 1)},
                ),
                html.Label("Wind Threshold (km/h)"),
                dcc.Slider(
                    id="wind-slider",
                    min=5,
                    max=50,
                    step=5,
                    value=10,
                    marks={i: str(i) for i in range(5, 51, 5)},
                ),
                html.Label("Cloud Threshold (%)"),
                dcc.Slider(
                    id="cloud-slider",
                    min=10,
                    max=100,
                    step=10,
                    value=50,
                    marks={i: str(i) for i in range(10, 101, 10)},
                ),
            ],
            style={"width": "50%", "margin": "auto"},
        ),
        dcc.Graph(id="weather_line", figure=initial_fig),  # Set initial figure
    ]
)


# callbacks
@app.callback(
    Output(component_id="weather_line", component_property="figure"),
    Input(component_id="checkboxes", component_property="value"),
    Input(component_id="temp-slider", component_property="value"),
    Input(component_id="wind-slider", component_property="value"),
    Input(component_id="cloud-slider", component_property="value"),
)
def update_line(selected_cities, temp_threshold, wind_threshold, cloud_threshold):
    updated_fig = plot_line(
        df,
        cities=selected_cities,
        temp_threshold=temp_threshold,
        wind_threshold=wind_threshold,
        cloud_threshold=cloud_threshold,
    )
    return updated_fig


if __name__ == "__main__":
    # application.run(host="127.0.0.0", debug=True)
    # application.run(host="0.0.0.0", port="800", debug=True)
    application.run(debug=True)
