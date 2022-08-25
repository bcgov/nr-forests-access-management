from fastapi import FastAPI
import os
import psycopg2

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
    return {"message": cursor.fetchone()}

app.include_router(api_router, prefix="/api/v1")
handler = Mangum(app)