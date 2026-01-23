import os
from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Conexión a MongoDB usando la variable de entorno que configuraste en Render
MONGO_URL = os.environ.get("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client.rastreador_db

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/update/{trailer_id}")
async def update_location(trailer_id: str, data: dict):
    # Guardamos cada punto en la base de datos con una marca de tiempo
    registro = {
        "trailer_id": trailer_id,
        "lat": data.get("lat"),
        "lng": data.get("lng"),
        "battery": data.get("battery"),
        "panic": data.get("panic", False),
        "timestamp": datetime.utcnow()
    }
    await db.posiciones.insert_one(registro)
    return {"status": "ok"}

@app.get("/fleet")
async def get_fleet():
    # Buscamos los trailers únicos registrados
    ids_trailers = await db.posiciones.distinct("trailer_id")
    estado_flota = {}
    
    for tid in ids_trailers:
        # Obtenemos el último punto conocido de este trailer
        cursor = db.posiciones.find({"trailer_id": tid}).sort("timestamp", -1).limit(1)
        ultimo = await cursor.to_list(length=1)
        
        if ultimo:
            # Obtenemos los últimos 30 puntos para la "estela" (trayectoria)
            historia_cursor = db.posiciones.find({"trailer_id": tid}).sort("timestamp", -1).limit(30)
            historia = await historia_cursor.to_list(length=30)
            camino = [[p["lat"], p["lng"]] for p in reversed(historia)]
            
            estado_flota[tid] = {
                "lat": ultimo[0]["lat"],
                "lng": ultimo[0]["lng"],
                "battery": ultimo[0].get("battery", "--"),
                "panic": ultimo[0].get("panic", False),
                "path": camino
            }
    return estado_flota