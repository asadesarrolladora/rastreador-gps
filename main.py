from fastapi import FastAPI, Request
from fastapi.responses import HTML5VideoResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Almacén temporal de la última ubicación
current_location = {"lat": 0, "lng": 0}

@app.get("/", response_class=HTMLResponse)
async def get_map(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/update")
async def update_location(data: dict):
    global current_location
    current_location = data
    print(f"Ubicación actualizada: {current_location}")
    return {"status": "ok"}

@app.get("/location")
async def get_location():
    return current_location

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
