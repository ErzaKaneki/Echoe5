import boto3

import environ
env = environ.Env()
environ.Env.read_env()

# Manually set the credentials
s3 = boto3.client(
    's3',
    aws_access_key_id=env('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=env('AWS_SECRET_ACCESS_KEY'),
    region_name=env('AWS_S3_REGION_NAME')
)

# List buckets to verify access
response = s3.list_buckets()
print(response)

s3.upload_file('django_blog_project/profile_pics/self2.jpeg', 'echoe5-files', 'profile_pics/self2.jpeg')