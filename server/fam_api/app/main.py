from fastapi import FastAPI
import os
import psycopg2
import boto3
import base64
from botocore.exceptions import ClientError

from app.api.api_v1.api import router as api_router
from mangum import Mangum

app = FastAPI()

@app.get("/")
async def root():
    connection = psycopg2.connect(host=os.environ.get('PG_HOST'),
                                  port=os.environ.get('PG_PORT'),
                                  user=os.environ.get('PG_USER'),
                                  password=os.environ.get('PG_PASSWORD'),
                                  dbname=os.environ.get('PG_DATABASE')
                                  )
    connection.autocommit = True  # Ensure data is added to the database immediately after write commands
    cursor = connection.cursor()
    cursor.execute('SELECT %s as connected;', ('Connection to postgres successful!',))
    return {"message": get_secret()}

def get_secret():

    secret_name = "fam_api_db_creds2"
    region_name = "ca-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    # else:
    #     # Decrypts secret using the associated KMS key.
    #     # Depending on whether the secret is a string or binary, one of these fields will be populated.
    #     if 'SecretString' in get_secret_value_response:
    #         secret = get_secret_value_response['SecretString']
    #     else:
    #         decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return get_secret_value_response['SecretString']   
    # Your code goes here. 


app.include_router(api_router, prefix="/api/v1")
handler = Mangum(app)