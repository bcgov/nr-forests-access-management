from fastapi import FastAPI
import os
import psycopg2
import boto3
import base64
import json

from app.api.api_v1.api import router as api_router
from mangum import Mangum

app = FastAPI()

@app.get("/")
async def root():
    secret_value = get_secret()
    secret_json = json.loads(secret_value['SecretString'])
    username = secret_json['username']
    password = secret_json['pasword']

    connection = psycopg2.connect(host=os.environ.get('PG_HOST'),
                                  port=os.environ.get('PG_PORT'),
                                  dbname=os.environ.get('PG_DATABASE'),
                                  user=username,
                                  password=password)
    connection.autocommit = True  # Ensure data is added to the database immediately after write commands
    cursor = connection.cursor()
    cursor.execute('SELECT %s as connected;', ('Connection to postgres successful!',))
    return {"message": cursor.fetchone()}

def get_secret():

    secret_name = os.environ.get('DB_SECRET')
    region_name = "ca-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    return client.get_secret_value( SecretId=secret_name )


app.include_router(api_router, prefix="/api/v1")
handler = Mangum(app)