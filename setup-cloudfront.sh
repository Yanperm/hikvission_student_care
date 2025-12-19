#!/bin/bash
# Setup CloudFront Distribution

echo "🚀 Setting up CloudFront..."

# Variables
ORIGIN_DOMAIN="43.210.87.220"
DOMAIN_NAME="yourdomain.com"  # แก้ไขเป็นโดเมนของคุณ

# 1. Request SSL Certificate
echo "📜 Requesting SSL Certificate..."
CERT_ARN=$(aws acm request-certificate \
  --domain-name "$DOMAIN_NAME" \
  --subject-alternative-names "www.$DOMAIN_NAME" "*.$DOMAIN_NAME" \
  --validation-method DNS \
  --region us-east-1 \
  --query 'CertificateArn' \
  --output text)

echo "Certificate ARN: $CERT_ARN"
echo "⚠️  Go to ACM Console and validate the certificate via DNS"
echo "Press Enter after DNS validation is complete..."
read

# 2. Create CloudFront Distribution
echo "☁️  Creating CloudFront Distribution..."

cat > cloudfront-config.json << EOF
{
  "CallerReference": "studentcare-$(date +%s)",
  "Comment": "Student Care System CDN",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "EC2-Origin",
        "DomainName": "$ORIGIN_DOMAIN",
        "CustomOriginConfig": {
          "HTTPPort": 5000,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "http-only"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "EC2-Origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 7,
      "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "ForwardedValues": {
      "QueryString": true,
      "Cookies": {
        "Forward": "all"
      },
      "Headers": {
        "Quantity": 1,
        "Items": ["Host"]
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 0,
    "MaxTTL": 0,
    "Compress": true
  },
  "Aliases": {
    "Quantity": 2,
    "Items": ["$DOMAIN_NAME", "www.$DOMAIN_NAME"]
  },
  "ViewerCertificate": {
    "ACMCertificateArn": "$CERT_ARN",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  },
  "PriceClass": "PriceClass_200"
}
EOF

DISTRIBUTION_ID=$(aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json \
  --query 'Distribution.Id' \
  --output text)

CLOUDFRONT_DOMAIN=$(aws cloudfront get-distribution \
  --id "$DISTRIBUTION_ID" \
  --query 'Distribution.DomainName' \
  --output text)

echo "✅ CloudFront Distribution Created!"
echo "Distribution ID: $DISTRIBUTION_ID"
echo "CloudFront Domain: $CLOUDFRONT_DOMAIN"
echo ""
echo "📋 Next Steps:"
echo "1. Go to your Domain Provider (Namecheap/GoDaddy)"
echo "2. Add CNAME record:"
echo "   Type: CNAME"
echo "   Name: www"
echo "   Value: $CLOUDFRONT_DOMAIN"
echo ""
echo "3. Add A record (if supported) or use www subdomain"
echo ""
echo "⏳ Wait 15-30 minutes for CloudFront to deploy"
echo "🌐 Then access: https://$DOMAIN_NAME"
