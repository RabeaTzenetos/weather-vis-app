import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def find_high_gradient_sections(data: pd.Series, threshold: float) -> list:
    """
    Find step changes larger than threshold to highlight in plotly fig
    """
    diff = np.diff(data)
    high_gradient_sections = []
    section_start = None

    for i, diff in enumerate(diff):
        if abs(diff) >= threshold:
            if section_start is None:
                section_start = i
        else:
            if section_start is not None:
                high_gradient_sections.append((section_start, i))
                section_start = None

    # check for ongoing high gradient section
    if section_start is not None:
        high_gradient_sections.append((section_start, len(data) - 1))

    return high_gradient_sections


def plot_line(
    df: pd.DataFrame,
    cities: list,
    temp_threshold: float = 2.5,
    wind_threshold: float = 10,
    cloud_threshold: float = 50,
):
    """
    Plot weather forecast data for given list of cities
    Highlights parts of the graph with step changes larger than the thresholds
    """
    # create subplots with shared x-axis
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        subplot_titles=(
            "Temperature (°C)",
            "Wind Speed (km/h)",
            "Cloud Cover (%)",
        ),
        vertical_spacing=0.06,
    )

    # initialize dict to store color and city label info
    color_map = {}
    color_idx = 0
    colors = px.colors.qualitative.Plotly

    # find maximum values for temperature, cloud cover, and wind speed across all cities
    max_temp = df["temperature_2m"].max()
    min_temp = df["temperature_2m"].min()
    max_cloud_cover = df["cloud_cover"].max()
    max_wind_speed = df["wind_speed_80m"].max()

    # for city in df["city"].unique():
    for city in cities:
        temp_df = df[df["city"] == city]

        if city not in color_map:
            color_map[city] = colors[color_idx % len(colors)]
            color_idx += 1

        color = color_map[city]

        fig.add_trace(
            go.Scatter(
                x=temp_df["date"],
                y=temp_df["temperature_2m"],
                mode="lines",
                name=city,
                line=dict(color=color),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=temp_df["date"],
                y=temp_df["wind_speed_80m"],
                mode="lines",
                name=city,
                line=dict(color=color),
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=temp_df["date"],
                y=temp_df["cloud_cover"],
                mode="lines",
                name=city,
                line=dict(color=color),
                showlegend=False,
            ),
            row=3,
            col=1,
        )

        # highlight sections with high gradient for temperature_2m
        high_gradient_sections_temp = find_high_gradient_sections(
            temp_df["temperature_2m"], temp_threshold
        )

        for start, end in high_gradient_sections_temp:
            fig.add_shape(
                type="rect",
                xref="x",
                yref="y",
                x0=temp_df["date"].iloc[start],
                y0=min_temp,
                x1=temp_df["date"].iloc[end],
                y1=max_temp,
                fillcolor="rgba(255, 0, 0, 0.3)",
                layer="below",
                line=dict(width=0),
                row=1,
                col=1,
            )

        # highlight sections with high gradient for wind_speed_80m
        high_gradient_sections_wind = find_high_gradient_sections(
            temp_df["wind_speed_80m"], wind_threshold
        )

        for start, end in high_gradient_sections_wind:
            fig.add_shape(
                type="rect",
                xref="x",
                yref="y",
                x0=temp_df["date"].iloc[start],
                y0=0,
                x1=temp_df["date"].iloc[end],
                y1=max_wind_speed,
                fillcolor="rgba(255, 0, 0, 0.3)",
                layer="below",
                line=dict(width=0),
                row=2,
                col=1,
            )
        # highlight sections with high gradient for cloud_cover
        high_gradient_sections_cloud = find_high_gradient_sections(
            temp_df["cloud_cover"], cloud_threshold
        )

        for start, end in high_gradient_sections_cloud:
            fig.add_shape(
                type="rect",
                xref="x",
                yref="y",
                x0=temp_df["date"].iloc[start],
                y0=0,
                x1=temp_df["date"].iloc[end],
                y1=max_cloud_cover,
                fillcolor="rgba(255, 0, 0, 0.3)",
                layer="below",
                line=dict(width=0),
                row=3,
                col=1,
            )

    fig.update_layout(
        title="Weather Metrics for Cities",
        showlegend=True,
        height=1000,
        xaxis_showticklabels=True,
        xaxis2_showticklabels=True,
    )
    fig.update_xaxes(title_text="Date", row=3, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Wind Speed (km/h)", row=2, col=1)
    fig.update_yaxes(title_text="Cloud Cover (%)", row=3, col=1)

    return fig
