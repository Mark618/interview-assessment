import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from app.api.routes import router
from app.ingestion.csv_loader import load_csv_to_db

CSV_PATH = "data/pricing_data.csv"
DATABASE_PATH = "app/database/database.db"



@asynccontextmanager
async def lifespan(app: FastAPI):
    os.remove(DATABASE_PATH)
    load_csv_to_db(CSV_PATH)
    yield
    

app = FastAPI(title="Pricing Intelligence API",lifespan=lifespan)

app.include_router(router)


@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")