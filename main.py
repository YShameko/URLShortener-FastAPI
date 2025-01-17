from urllib import request

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()


@app.get("/")
async def root():
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
