import boto3
import os
from lambda_tasks import get_meteo_weather_data


# AWS credentials
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")


def lambda_handler(event, context):  # add event and context inputs when deploying
    """
    Lambda csv upload to S3 bucket
    """
    bucket_name = "elasticbeanstalk-us-east-2-780026431059"
    file_key = "forecast.csv"
    df = get_meteo_weather_data()
    csv_buffer = df.to_csv(index=False)

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    # upload CSV content to the existing S3 bucket
    s3.put_object(Body=csv_buffer, Bucket=bucket_name, Key=file_key)

    return {"statusCode": 200, "body": "Lambda function executed successfully"}


lambda_handler()
