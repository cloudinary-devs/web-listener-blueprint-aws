'''
The cldListener blueprint. Read further here: https://cloudinary.com/blog/a_blueprint_for_aws_secured_webhook_listeners_for_cloudinary
'''
import logging
import json
from urllib.error import HTTPError
from cloudinary import uploader, exceptions
from cldListenerUtils import validate_signature, config_cloudinary_instance, exception_wrapper

def set_logger():
    ''' Set your favorite logger
    '''
    global logger
    logger = logging.getLogger('cld')
    logger.setLevel(logging.INFO)

def main_process(payload):
    ''' The main process: Check if the Hello World! tag exists, otherwise append it
    '''
    try:
        config_cloudinary_instance()
        tags = list(payload.get('tags', ''))
        hello_world = 'Hello World!'
        if hello_world not in tags:
            tags.append(hello_world)
        uploader.explicit(payload['public_id'], 
            type = payload['type'],
            resource_type = payload['resource_type'],
            tags = tags
        )
    except exceptions.Error as e:
        raise HTTPError(None, 400, e, None, None)

def lambda_handler(event, context):
    ''' The lambda entry point
    '''
    try:
        set_logger()
        logger.info(json.dumps(event))
        # each event notification sent from your Cloudinary account is cryptographically signed
        validate_signature(event)
        main_process(json.loads(event['body']))
    except Exception as e:
        return exception_wrapper(logger, e)
    return {'statusCode': 200, 'body': 'OK', 'isBase64Encoded': False}
