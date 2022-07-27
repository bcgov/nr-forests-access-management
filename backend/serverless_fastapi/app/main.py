from fastapi import FastAPI

from app.api.api_v1.api import router as api_router

app = FastAPI()


@app.get("/")
async def root():
  return {"message": "Hello World"}

app.include_router(api_router, prefix="/api/v1")
