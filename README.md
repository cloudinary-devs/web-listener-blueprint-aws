# Cloudinary

Cloudinary is a powerful media API for websites and mobile apps. We enable developers to efficiently work with media 
assets at every stage of the process, including managing, transforming, optimizing, and delivering images and videos 
via multiple CDNs. Cloudinary provides responsive, personalized, visual media experiences to viewers on any device.

## Description

An easy-to-use Cloudinary listener that enables almost any type of extension to the Cloudinary solution. The package is installed on AWS using the Cloudformation service.
The implemented extension is adding the tag 'Hello World!' to any newly uploaded asset.

## Prerequisites

To create a blueprint for a Cloudinary webhook listener, you need the following:

* [A Cloudinary account](https://cloudinary.com/console)
* [An AWS account](https://aws.amazon.com/console/)
* [The AWS command-line interface (CLI)](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
* S3 bucket to host artifacts uploaded by CloudFormation e.g. Lambda ZIP deployment packages
You can use the following command to create the Amazon S3 bucket, say in us-east-1 region
```
export my_bucket=<my-bucket-name>
aws s3 mb s3://$my_bucket --region us-east-1
aws s3api put-bucket-encryption \
    --bucket $my_bucket \           
    --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
aws s3api put-public-access-block \
    --bucket $my_bucket \
    --public-access-block-configuration '{"BlockPublicAcls": true, "IgnorePublicAcls": true, "BlockPublicPolicy": true, "RestrictPublicBuckets": true}'
```

## Installing

1. Upload all the repository ZIP files to your bucket or [create the ZIP files yourself](#optional---create-packages-from-sources)
```
aws s3 cp cldListenerUtils.zip s3://$my_bucket
aws s3 cp CloudinarySDK.zip s3://$my_bucket
aws s3 cp index.zip s3://$my_bucket
```

2. Create a Cloudformation stack
Use the [AWS Management Console](https://console.aws.amazon.com/cloudformation/home) to import the file serverless.yml, or use the below CLI which needs a bit higher user's permission level.
```
aws cloudformation deploy \
    --region us-east-1 \
    --template serverless.yml \
    --stack-name CloudinaryListener \
    --s3-bucket $my_bucket \
    --parameter-overrides CloudinaryListenerS3='$my_bucket' CloudinaryListenerUploadPrefix='https://api.cloudinary.com' \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
```

3. Config the new web listener in Cloudinary
- Check the Outputs section of the new Cloudformation stack and copy the cldListenerAPI. 
- Paste the URL into an Upload Preset Notification URL in the Cloudinary console [upload preset](https://cloudinary.com/console/settings/upload)

4. Config the Cloudinary credentials in AWS
- Copy the environment variable from the Cloudinary [web console dashboard](https://cloudinary.com/console). You need to be the sub-account admin. Click on "reveal account details" in order to expose the environment variable.
- Go to the AWS [SecretsManager](https://console.aws.amazon.com/secretsmanager/home), edit the secret cldListenerSecret, and paste the environment variable to the secret's value.

## Testing
1. Make sure that the configured upload preset is the default for ML or API uploads
2. Upload an asset to Cloudinary
3. Check that the asset got the "Hello World!" tag
4. Check Cloudwatch for the created log entries

## Optional - create packages from sources
Here we create the different Lambda layers. This is useful when need to upgrade the current libs, add additional libs, or redistribute the main app code (for a colleague, or your IT DevOps team).

    mkdir python
    python3 -m pip install --target ./python cloudinary
    zip -r9 CloudinarySDK.zip python
    rm -rf python/*
    cp cldListenerUtils.py python
    zip -r9 cldListenerUtils.zip python
    rm -rf python/*
    zip -j9 index.zip index.py
Upload all ZIP files to your source bucket as specified in the [Installing](#installing) section, step #1.

## Files in distribution
* CloudinarySDK.zip - The Cloudinary Python SDK packaged as an AWS Lambda Layer
* cldListenerUtils.py - A wrapper of the Cloudinary SDK and AWS SDK for abstraction and simplification of the web listener code
* cldListenerUtils.zip - The above wrapper packaged as an AWS Lambda Layer
* index.py - the blueprint sample code
* index.zip - the above sample code packaged as an AWS Lambda code
* testEvent.json - This is a test event to associate with the web listener Lambda, to allow unit testing
* serverless.yml - the cloudformation template
