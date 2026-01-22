from fastapi.responses import HTMLResponse
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from fastapi.templating import Jinja2Templates
import app.agent.service as service

router = APIRouter()
template = Jinja2Templates(directory = "app/templates")

@router.get("/", response_class = HTMLResponse)
async def home(request: Request):
    return template.TemplateResponse("index.html", {"request": request})  

@router.post("/upload-file/")
async def upload_file(file: UploadFile = File()):
    return await service.upload_file(file)

@router.get("/ask/")
async def ask_question(query: str):
    return await service.ask_question(query)