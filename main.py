import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()

# Configuración robusta de carpetas para la nube
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(current_file_path)
templates_path = os.path.join(project_root, "templates")

templates = Jinja2Templates(directory=templates_path)

# Almacén de ubicación
current_location = {"lat": 0, "lng": 0}

@app.get("/", response_class=HTMLResponse)
async def get_map(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/update")
async def update_location(data: dict):
    global current_location
    current_location = data
    return {"status": "ok"}

@app.get("/location")
async def get_location():
    return current_location

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)