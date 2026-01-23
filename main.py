import os
from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.templating import Jinja2Templates
from datetime import datetime
import pytz # Para manejar la hora local de México

app = FastAPI()
templates = Jinja2Templates(directory="templates")

MONGO_URL = os.environ.get("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client.rastreador_db

# Configuración de zona horaria (CDMX)
mexico_tz = pytz.timezone('America/Mexico_City')

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/update/{trailer_id}")
async def update_location(trailer_id: str, data: dict):
    ahora = datetime.now(mexico_tz)
    
    registro = {
        "trailer_id": trailer_id,
        "lat": data.get("lat"),
        "lng": data.get("lng"),
        "battery": data.get("battery"),
        "panic": data.get("panic", False),
        "timestamp": ahora,
        "hora_lectura": ahora.strftime("%H:%M:%S") 
    }
    await db.posiciones.insert_one(registro)
    return {"status": "ok"}

@app.get("/fleet")
async def get_fleet():
    ids_trailers = await db.posiciones.distinct("trailer_id")
    estado_flota = {}
    
    for tid in ids_trailers:
        cursor = db.posiciones.find({"trailer_id": tid}).sort("timestamp", -1).limit(1)
        ultimo = await cursor.to_list(length=1)
        
        if ultimo:
            historia_cursor = db.posiciones.find({"trailer_id": tid}).sort("timestamp", -1).limit(50)
            historia = await historia_cursor.to_list(length=50)
            camino = [[p["lat"], p["lng"]] for p in reversed(historia)]
            
            estado_flota[tid] = {
                "lat": ultimo[0]["lat"],
                "lng": ultimo[0]["lng"],
                "battery": ultimo[0].get("battery", "--"),
                "panic": ultimo[0].get("panic", False),
                "last_seen": ultimo[0].get("hora_lectura", "--:--"),
                "path": camino
            }
    return estado_flota