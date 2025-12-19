# S3 Storage Manager
import boto3
import os
from datetime import datetime

class S3Storage:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.bucket = os.environ.get('S3_BUCKET', 'studentcare-files')
    
    def upload_student_image(self, student_id, image_data):
        """Upload student image to S3"""
        try:
            key = f"students/{student_id}.jpg"
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=image_data,
                ContentType='image/jpeg'
            )
            return f"s3://{self.bucket}/{key}"
        except Exception as e:
            print(f"S3 Upload Error: {e}")
            return None
    
    def get_student_image(self, student_id):
        """Get student image from S3"""
        try:
            key = f"students/{student_id}.jpg"
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
        except Exception as e:
            print(f"S3 Download Error: {e}")
            return None
    
    def delete_student_image(self, student_id):
        """Delete student image from S3"""
        try:
            key = f"students/{student_id}.jpg"
            self.s3.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception as e:
            print(f"S3 Delete Error: {e}")
            return False

# Initialize
s3_storage = S3Storage()
