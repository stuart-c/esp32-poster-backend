import boto3
import json
import os
import io

class AWSContext:
    def __init__(self):
        # Allow connecting to localstack if DEV mode
        endpoint_url = os.getenv("AWS_ENDPOINT_URL")
        self.s3 = boto3.client('s3', endpoint_url=endpoint_url)
        self.dynamodb = boto3.resource('dynamodb', endpoint_url=endpoint_url)
        
    def download_image(self, bucket: str, key: str) -> bytes:
        response = self.s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()

    def upload_display_image(self, bucket: str, key: str, img_data: bytes, content_type: str = 'image/bmp'):
        self.s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=img_data,
            ContentType=content_type,
            CacheControl='max-age=3600'
        )

    def upload_manifest(self, bucket: str, key: str, manifest: dict):
        self.s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(manifest),
            ContentType='application/json',
            CacheControl='max-age=60'
        )

    def get_presentation(self, table_name: str, presentation_id: str) -> dict:
        table = self.dynamodb.Table(table_name)
        response = table.get_item(Key={'id': presentation_id})
        return response.get('Item')

    def get_layout(self, table_name: str, layout_id: str) -> dict:
        table = self.dynamodb.Table(table_name)
        response = table.get_item(Key={'id': layout_id})
        return response.get('Item')

    def update_presentation_status(self, table_name: str, presentation_id: str, status: str, result_s3_prefix: str = None):
        table = self.dynamodb.Table(table_name)
        update_exp = "SET #st = :s"
        exp_vals = {':s': status}
        if result_s3_prefix:
            update_exp += ", result_prefix = :p"
            exp_vals[':p'] = result_s3_prefix
            
        table.update_item(
            Key={'id': presentation_id},
            UpdateExpression=update_exp,
            ExpressionAttributeNames={'#st': 'status'},
            ExpressionAttributeValues=exp_vals
        )
