import sys
import os.path
import boto3
from botocore.exceptions import ClientError
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def initializeS3Client(end_point):
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=end_point,
            aws_access_key_id='test',
            aws_secret_access_key='test',
        )
        logging.info("S3 client initialized successfully")
        return s3_client
    except ClientError as e:
        logging.error(f"S3 client initialization error: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while S3 client initialization: {e}")
        return None

def initializeBucket(s3_client, bucket_name):
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'}
        )
        logging.info(f"Bucket '{bucket_name}' created successfully!")
    except ClientError as e:
        if e.response['Error']['Code'] == "BucketAlreadyOwnedByYou":
            logging.error(f"Bucket '{bucket_name}' is already created!")
        else:
            logging.error(f"Bucket error: {e.response['Error']['Code']}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while bucket '{bucket_name}' creation: {e}")

def listBuckets(s3_client):
    logging.info('Existing buckets:')
    for bucket in s3_client.list_buckets()['Buckets']:
        logging.info(f'{bucket["Name"]}')

def listFiles(s3_client, bucket_name):
    logging.info('Files in the bucket:')
    try:
        files = s3_client.list_objects_v2(Bucket=bucket_name).get('Contents', [])
        for file_name in [file['Key'] for file in files]:
            logging.info(file_name)
    except ClientError as e:
        logging.error(f"Failed to list files: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while listing files: {e}")

def uploadFile(s3_client, bucket_name, file_path):
    try:
        with open(file_path, 'rb') as fileobj:
            s3_client.upload_fileobj(fileobj, bucket_name, os.path.basename(fileobj.name))
        logging.info(f"File '{fileobj.name}' uploaded successfully!")
    except FileNotFoundError as e:
        logging.error(f"File at path '{file_path}' not found")
    except ClientError as e:
        logging.error(f"Failed to upload file '{os.path.basename(fileobj.name)}': {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while uploading '{os.path.basename(fileobj.name)}': {e}")

def deleteFile(s3_client, bucket_name, file_name):
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        logging.info(f"File '{file_name}' deleted successfully!")
    except ClientError as e:
        logging.error(f"An error occurred while deleting file '{file_name}': {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while deleting file '{file_name}': {e}")

def getDownloadURL(s3_client, bucket_name, file_name):
    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        logging.info(f"Generation of a presigned URL to download a file {file_name} is successful")
        return presigned_url
    except ClientError as e:
        logging.error(f"An error occurred while generating the download link for {file_name}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while generating the download link for {file_name}: {e}")
        return None

# def main():
#     end_point = 'http://localhost:4566' # change endpoint to the proper one
#     s3_client = initializeS3Client(end_point)
#     if s3_client:
#         try:
#             # Initialize the bucket
#             bucket_name = 'mybucket'
#             initializeBucket(s3_client, bucket_name)

#             # Output the existing buckets' names
#             listBuckets(s3_client)
        
#             # # Upload the file
#             # file_path = './tmp/example2.txt'
#             # uploadFile(s3_client, bucket_name, file_path)
            
#             # List files
#             listFiles(s3_client, bucket_name)
            
#             # # Delete the file
#             # file_name = 'name'
#             # deleteFile(s3_client, bucket_name, file_name)
            
#             # # Download the file
#             # file_name = 'example.txt'
#             # print(getDownloadURL(s3_client, bucket_name, file_name))

#         except Exception as e:
#             logging.error(f"Error in main: {e}")
# main()
