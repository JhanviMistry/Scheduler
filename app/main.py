from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.agent.controller import router

app = FastAPI()
app.mount("/static", StaticFiles(directory = "app/static"), name = "static")

#setup routes
app.include_router(router)