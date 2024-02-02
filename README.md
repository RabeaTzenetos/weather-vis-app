# Weather Visualisation
http://weather-vis.us-east-2.elasticbeanstalk.com/

Weather Vis is an AWS Elastic Beanstalk Application that shows an hourly granularity 7-day weather forecast for a number of European cities.
The plotly dashboard highlights periods in which the change from one hour to the next exceeds the user-specified thresholds. 

### Underlying Data
The data is pulled from Open-Meteo API and includes temperature, wind speed, and cloud cover. Data is updated every hour on the hour. 

### AWS Services
- **EC2 Instance**: Environment and virtual machine
- **Elastic Beanstalk**: Hosts and deploys Dash application
- **S3 Bucket**: Holds Python files and latest weather forecast data
- **Lambda**: Retrieves new weather forecast data
- **CloudWatch**: Schedules Lambda function

### Deployments
New versions can be deployed by pushing/merging to the main branch of this repo.\
Note that the `.github/workflow/deployment.yml` needs to be amended to include a new version-label.

```yaml
name: Deploy to AWS Elastic Beanstalk
run: |
  aws elasticbeanstalk create-application-version \
    --application-name weather-vis \
    --version-label layout-cleanup1 \
    --source-bundle S3Bucket=elasticbeanstalk-us-east-2-780026431059,S3Key=weather.zip \
    --debug

  aws elasticbeanstalk update-environment \
    --environment-name Weather-vis-env-2 \
    --version-label layout-cleanup1 \
    --debug
```

### Notes to Self
##### Lambda
- Linked to `weather-lambda` layer which in turn is linked to the `python.zip` file in S3 bucket which holds the unzipped `.whl` files from https://pypi.org/
- If Lambda functionality requires additional libraries in the future, the `.whl` contents will need to be added to the layer. Use `manylinux[...]x84_64` file versions for compatibility with AWS Lambda function.

##### Error Logs
- Logs containing information on application errors (e.g. webpage shows 502) can be found in `management console > environment > log`, select between full and tail

##### EC2 Connection & Files
- ssh -i "weather-vis-key.pem" ec2-user@ec2-XX-XXX-XXX-XXX.us-east-2.compute.amazonaws.com
