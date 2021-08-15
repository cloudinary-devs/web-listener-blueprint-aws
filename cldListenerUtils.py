'''
The cldListener utility module provides
the necessities of (almost) each Lambda function that listens
to Cloudinary event.
It is implemented as a layer in the cldListener blueprint
'''

import hashlib
import boto3
import json
from os import environ
from time import time
from urllib3.util import parse_url
from urllib.error import HTTPError
from cloudinary import config

def get_secret():
    ''' get "API Environment variable" from https://cloudinary.com/console/ -> Account Details
        Cache the requests to SecretManager for performance and budget optimization
    '''
    global cloudinary_url, api_secret
    if not 'cloudinary_url' in globals():
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=environ['AWS_REGION']
        )
        secrets = json.loads(client.get_secret_value(SecretId=environ['secret_name'])['SecretString'])
        cloudinary_url = []
        cloudinary_url.append(secrets[environ['secret_selector']].split('=')[1])
        if 'secret_selector_2' in environ:
            cloudinary_url.append(secrets[environ['secret_selector_2']].split('=')[1])
        api_secret = []
        api_secret.append(parse_url(cloudinary_url[0]).auth.split(':')[1])
        if 'secret_selector_2' in environ:
            api_secret.append(parse_url(cloudinary_url[1]).auth.split(':')[1])
    return cloudinary_url, api_secret

def validate_signature(request):
    ''' Validate that the received notification was really sent from Cloudinary
    '''
    payload_to_sign = request['body']
    cloudinary_url, api_secret = get_secret()
    headers = request['headers']
    x_cld_timestamp = headers.get('X-Cld-Timestamp',"")
    if headers['X-Forwarded-Port'] != 'cld-test' and (float(x_cld_timestamp) > time() + 200 or float(x_cld_timestamp) < time() - 200):
        raise HTTPError(None, 417, 'Failed timestamp validation', None, None)
    x_cld_signature = headers.get('X-Cld-Signature', "")
    to_sign = payload_to_sign + x_cld_timestamp + api_secret[0]
    if hashlib.sha1(to_sign.encode('utf-8')).hexdigest() != x_cld_signature:
        raise HTTPError(None, 403, 'Invalid signature', None, None)

def config_cloudinary_instance(i = 0):
    ''' Get a cloudinary config instance
    '''
    cloudinary_url, api_secret = get_secret()
    cld_config = parse_url(cloudinary_url[i])
    config(  
        cloud_name = cld_config.host, 
        api_key = cld_config.auth.split(':')[0], 
        api_secret = api_secret[i],
        upload_prefix=environ['upload_prefix']
    )

def exception_wrapper(logger, e):
    ''' Nicely wrapping exceptions to return as a standard HTTP response
    '''
    code = 500
    reason = str(e)
    try:
        code = int(e.code)
    except Exception:
        pass
    try:
        reason = str(e.reason)
    except Exception:
        pass
    try:
        logger.error("{0}-{1}".format(code, reason))
    except Exception:
        print("Error: cannot use logger. Possibly caused by: {0}-{1}".format(code, reason))
    return {'statusCode': code, 'body': reason, 'isBase64Encoded': False}
