import os
import string
from typing import Annotated

import aiofiles
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
import random
import json

# -----------------------------------------------------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")
db_name = 'urls.json'
# -----------------------------------------------------------
@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/")
async def root(long_url: Annotated[str, Form()]):
    short_url = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(5)])
    # if 'db_name' does not exist, we created this file
    if not os.path.isfile(db_name):
        with open(db_name, 'w') as f:   f.write("{}")

    async with aiofiles.open(db_name, 'r') as f:
        existing_data = json.loads(await f.read())
    async with aiofiles.open(db_name, 'w') as f:
        existing_data[short_url] = long_url
        await f.write(json.dumps(existing_data, indent=4))

    return f"Your shortened URL is: /{short_url}"

@app.get("/{short_url}")
async def convert_url(short_url: str):
    async with aiofiles.open(db_name, 'r') as f:
        redirect_url = json.loads(await f.read()).get(short_url)
    if redirect_url is None:
        raise HTTPException(status_code=404, detail="This URL does not exist")
    else:
        return RedirectResponse(redirect_url)