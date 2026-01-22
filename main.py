import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Estado global del dispositivo
device_status = {
    "lat": 0, 
    "lng": 0, 
    "alert": False, 
    "panic": False,
    "battery": "--"
}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/update")
async def update_location(data: dict):
    global device_status
    # Actualizamos solo los campos que vengan en el envío
    device_status.update(data)
    return {"status": "ok"}

@app.get("/location")
async def get_location():
    return device_status

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)