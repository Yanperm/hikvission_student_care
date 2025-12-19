#!/usr/bin/env python3
"""
Deploy to S3 Static Website
© 2025 SOFTUBON CO.,LTD.
"""

import boto3
import os
from pathlib import Path

# AWS Configuration
BUCKET_NAME = 'student-care-system'
REGION = 'ap-southeast-1'

def upload_to_s3():
    s3 = boto3.client('s3', region_name=REGION)
    
    # Create bucket
    try:
        s3.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={'LocationConstraint': REGION}
        )
        print(f"✅ Created bucket: {BUCKET_NAME}")
    except:
        print(f"ℹ️ Bucket already exists: {BUCKET_NAME}")
    
    # Enable static website hosting
    s3.put_bucket_website(
        Bucket=BUCKET_NAME,
        WebsiteConfiguration={
            'IndexDocument': {'Suffix': 'index.html'},
            'ErrorDocument': {'Key': 'error.html'}
        }
    )
    
    # Upload files
    folders = ['templates', 'static']
    for folder in folders:
        for file_path in Path(folder).rglob('*'):
            if file_path.is_file():
                key = str(file_path).replace('\\', '/')
                s3.upload_file(str(file_path), BUCKET_NAME, key)
                print(f"📤 Uploaded: {key}")
    
    print(f"\n🎉 Deployed to: http://{BUCKET_NAME}.s3-website-{REGION}.amazonaws.com")

if __name__ == '__main__':
    upload_to_s3()
