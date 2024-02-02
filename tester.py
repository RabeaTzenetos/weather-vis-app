import pandas as pd

# from lambda_function.lambda_tasks import get_meteo_weather_data
# from lambda_function.lambda_handler import lambda_handler


# df = get_meteo_weather_data()
# print(df.head())
# df.to_csv("forecast.csv")
# df = pd.read_csv("forecast-overwrite.csv", parse_dates=["date"]).drop(
#     columns="Unnamed: 0", errors="ignore"
# )

# plot_line(
#     df,
#     cities=["London", "Paris"],
#     temp_threshold=2,
#     wind_threshold=10,
#     cloud_threshold=20,
# ).show()

# lambda_handler()  # add event and context back in
