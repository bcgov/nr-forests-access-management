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

    ENDPOINT=os.environ.get('PG_HOST')
    PORT=os.environ.get('PG_PORT')
    USER=os.environ.get('PG_USER')
    # Currently, all proxies listen on port 5432 for RDS PostgreSQL
    REGION=5432
    DBNAME=os.environ.get('PG_DATABASE')

    session = boto3.Session(profile_name='RDSCreds')
    client = session.client('rds')
    token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)
    connection = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=token, sslrootcert="SSLCERTIFICATE")

    connection.autocommit = True  # Ensure data is added to the database immediately after write commands
    cursor = connection.cursor()
    cursor.execute("select app.application_description from app_fam.fam_application app where app.application_name = 'fam';")
    return {"message": cursor.fetchone()}

app.include_router(api_router, prefix="/api/v1")
handler = Mangum(app)