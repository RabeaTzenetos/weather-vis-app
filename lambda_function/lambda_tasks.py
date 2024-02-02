import pandas as pd
from geopy.geocoders import Nominatim
import openmeteo_requests

from consts import cities

# import requests_cache
# from retry_requests import retry


def get_city_coords(cities: list) -> list:
    """
    Retrieves coordinate information for list of cities
    """

    geolocator = Nominatim(user_agent="test")
    locations = []

    for city in cities:
        location = geolocator.geocode(city)
        dict_helper = {
            "city": city,
            "lat": location.latitude,
            "long": location.longitude,
        }
        locations.append(dict_helper)

    return locations


def get_meteo_weather_data(
    parameters: list = ["temperature_2m", "cloud_cover", "wind_speed_80m"]
) -> pd.DataFrame:
    """
    Retrieve weather forecast data from open-meteo
    """
    # Setup the Open-Meteo API client with cache and retry on error

    # cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    # retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    # openmeteo = openmeteo_requests.Client(session=retry_session)
    openmeteo = openmeteo_requests.Client()

    locations = get_city_coords(cities)

    url = "https://api.open-meteo.com/v1/forecast"
    dfs = []

    for location in locations:
        params = {
            "latitude": location["lat"],
            "longitude": location["long"],
            "hourly": parameters,
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()
        hourly_wind_speed_80m = hourly.Variables(2).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s"),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left",
            )
        }
        hourly_data["city"] = location["city"]
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["cloud_cover"] = hourly_cloud_cover
        hourly_data["wind_speed_80m"] = hourly_wind_speed_80m

        df_hourly = pd.DataFrame(data=hourly_data)
        dfs.append(df_hourly)

    df = pd.concat(dfs)
    return df
