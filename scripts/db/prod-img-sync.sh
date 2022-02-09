#!/bin/bash
aws --profile anika s3 sync --acl public-read s3://anika-clerk/images s3://anika-clerk-test/images
aws --profile anika s3 sync s3://anika-clerk/original_images/ s3://anika-clerk-test/original_images/
aws --profile anika s3 sync --acl public-read s3://anika-clerk/file-uploads s3://anika-clerk-test/file-uploads
aws --profile anika s3 sync --acl public-read s3://anika-clerk/action-documents s3://anika-clerk-test/action-documents
aws --profile anika s3 sync --acl public-read s3://anika-clerk/email-attachments s3://anika-clerk-test/email-attachments
