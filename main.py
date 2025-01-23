import os
import string
from typing import Annotated
from urllib import request

import aiofiles
import pymongo
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
import random
import json
import motor.motor_asyncio

# -----------------------------------------------------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")
db_client = motor.motor_asyncio.AsyncIOMotorClient("localhost", 27017, username="root", password="example")
app_db = db_client["url_shortener"]
collection = app_db["urls"]
# -----------------------------------------------------------
@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/")
async def root(long_url: Annotated[str, Form()]):
    short_url = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(5)])
    await collection.insert_one({"short_url": short_url, "long_url": long_url})

    return f"Your shortened URL is: /{short_url}"

@app.get("/{short_url}")
async def convert_url(short_url: str):
    collection_data = await collection.find_one({"short_url": short_url})
    redirect_url = collection_data.get("long_url") if collection_data else None
    if redirect_url is None:
        raise HTTPException(status_code=404, detail="This URL does not exist")
    else:
        await collection.update_one({"short_url": short_url}, {"$inc": {"clicks": 1}})
        return RedirectResponse(redirect_url)

@app.get("/{short_url}/stats")
async def stats(request:Request, short_url: str):
    collection_data = await collection.find_one({"short_url": short_url})
    if collection_data is None:
        raise HTTPException(status_code=404, detail="This URL does not exist")
    return templates.TemplateResponse(request=request, name="stats.html", context={"url_data": collection_data})

@app.post("/{short_url}/stats")
async def edit_stats(request: Request, short_url: str, long_url: Annotated[str, Form()]):
    await collection.update_one({"short_url": short_url}, {"$set":{"long_url":long_url}})
    collection_data = await collection.find_one({"short_url": short_url})
    return templates.TemplateResponse(request=request, name="stats.html", context={"url_data": collection_data})
