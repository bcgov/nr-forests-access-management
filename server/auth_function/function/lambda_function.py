import os
import logging
import jsonpickle
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))

    # grab requestor's email address
    email = event['request']['userAttributes']['email']
    
    # placeholder variable
    pet_preference = ''
    
    # set preference to 'dogs' if email contains @amazon.com
    # otherwise preference is 'cats'
    if "@amazon.com" in email:
        pet_preference = 'dogs'
    else:
        pet_preference = 'cats'
    
    # this allows us to override claims in the id token
    # "claimsToAddOrOverride" is the important part 
    event["response"]["claimsOverrideDetails"] = { 
        "claimsToAddOrOverride": { 
            "pet_preference": pet_preference 
            }
        } 

    return event
