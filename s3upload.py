import sys
import boto3

from definitions import S3_Bucket


s3_bucket_name = S3_Bucket
upload_fname = s3_fname = sys.argv[1]

s3_resource = boto3.resource('s3')
s3object = s3_resource.Object(s3_bucket_name, upload_fname)
s3object.upload_file(upload_fname, ExtraArgs={'ServerSideEncryption': 'AES256'})
