#!/bin/bash

# ต้องติดตั้ง AWS CLI และ configure credentials ก่อน
# aws configure

# หา Web ACL ID
WEB_ACL_ID=$(aws wafv2 list-web-acls --scope CLOUDFRONT --region us-east-1 --query 'WebACLs[0].Id' --output text)
WEB_ACL_NAME=$(aws wafv2 list-web-acls --scope CLOUDFRONT --region us-east-1 --query 'WebACLs[0].Name' --output text)

echo "Web ACL ID: $WEB_ACL_ID"
echo "Web ACL Name: $WEB_ACL_NAME"

# Get lock token
LOCK_TOKEN=$(aws wafv2 get-web-acl --scope CLOUDFRONT --region us-east-1 --id $WEB_ACL_ID --name $WEB_ACL_NAME --query 'LockToken' --output text)

# เพิ่ม Rule
aws wafv2 update-web-acl \
  --scope CLOUDFRONT \
  --region us-east-1 \
  --id $WEB_ACL_ID \
  --name $WEB_ACL_NAME \
  --lock-token $LOCK_TOKEN \
  --rules '[
    {
      "Name": "AllowStudentRegistration",
      "Priority": 0,
      "Statement": {
        "OrStatement": {
          "Statements": [
            {
              "ByteMatchStatement": {
                "SearchString": "/add_student",
                "FieldToMatch": {
                  "UriPath": {}
                },
                "TextTransformations": [
                  {
                    "Priority": 0,
                    "Type": "NONE"
                  }
                ],
                "PositionalConstraint": "STARTS_WITH"
              }
            },
            {
              "ByteMatchStatement": {
                "SearchString": "/api/self_register",
                "FieldToMatch": {
                  "UriPath": {}
                },
                "TextTransformations": [
                  {
                    "Priority": 0,
                    "Type": "NONE"
                  }
                ],
                "PositionalConstraint": "STARTS_WITH"
              }
            }
          ]
        }
      },
      "Action": {
        "Allow": {}
      },
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "AllowStudentRegistration"
      }
    }
  ]'

echo "✅ WAF Rule added successfully!"
