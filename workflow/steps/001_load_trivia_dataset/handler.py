import sandgarden_runtime
import requests
import botocore

def handler(input, sandgarden, runtime_context):
    bucket_name = "sandgarden-trivia-challenge"
    key = "har_dataset.jsonl"
    
    # Initialize S3 module
    sandgarden_runtime.initialize_modules(['sandgarden-trivia-challenge'], sandgarden)
    s3 = sandgarden.modules['sandgarden-trivia-challenge']['s3']
    
    # Check if the key exists in the bucket
    try:
        s3.head_object(Bucket=bucket_name, Key=key)
        return  # Key exists, return early
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] != '404':
            raise  # If the error is not a 404, re-raise it
    
    # Fetch the dataset
    url = "https://raw.githubusercontent.com/google-research-datasets/cf_triviaqa/refs/heads/main/har_dataset.jsonl"
    response = requests.get(url)
    dataset = response.text
    
    # Save the dataset to S3
    s3.put_object(Bucket=bucket_name, Key=key, Body=dataset)
    
    return
