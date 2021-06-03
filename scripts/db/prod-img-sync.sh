#!/bin/bash
aws --profile anika s3 sync --acl public-read s3://anika-clerk/images s3://anika-clerk-test/images
aws --profile anika s3 sync s3://anika-clerk/original_images/ s3://anika-clerk-test/original_images/
